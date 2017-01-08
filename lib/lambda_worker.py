from __future__ import print_function
from utils import kp_dumps, kp_loads
import boto3
from redis import StrictRedis
import os
import json
import redis_lock
import requests

from worker import read_base64, calc_diff, generate_descriptor


def prt(context):
    print(context.get_remaining_time_in_millis())


def get_redis():
    elastic_ip = os.environ['ELASTICACHE_IP']
    elastic_port = os.getenv('ELASTICACHE_PORT', '6379')

    print('Connecting to Redis at:', elastic_ip, elastic_port)

    # nodes = elasticache_auto_discovery.discover(elastic_endpoint)
    # nodes = map(lambda x: {'host': x[1], 'port': x[2]}, nodes)
    redis_conn = StrictRedis(
        host=elastic_ip,
        port=int(elastic_port),
        socket_connect_timeout=2
    )

    print('Started connection to Redis.')

    return redis_conn


REDIS_CONN = get_redis()
MATCH = 'cattle_image_id_*'


def get_descriptor_from_event(event, context, prefix=None):
    s3_info = event['Records'][0]['s3']
    s3_bucket = s3_info['bucket']['name']
    s3_key = s3_info['object']['key']

    print('Image put:', s3_bucket, s3_key)
    print('Retrieving image from S3')
    prt(context)

    s3_client = boto3.client('s3')
    image = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)['Body'].read()

    print('Retrieved image from S3')
    prt(context)

    id_ = s3_key.split('/')[-1].split('-')[0]

    print('Event ID:', id_)
    print('Generating image descriptor')
    prt(context)

    image_array = read_base64(image)
    image_descriptor = generate_descriptor(image_array)

    print('Generated image descriptor. Sending to Redis.')
    prt(context)

    if prefix is not None:
        REDIS_CONN.set('%s%s' % (prefix, id_), kp_dumps(image_descriptor))

    print('Sent to Redis successfully.')
    prt(context)

    return id_, image_descriptor, s3_client


def register_handler(event, context):
    get_descriptor_from_event(event, context, prefix='cattle_image_id_')
    return {'status': 'success'}


def match_handler(event, context):
    match_image_id, match_image_descriptor, s3_client = get_descriptor_from_event(event, context, prefix='match_image_id_')

    print('Invoking lambda comparisons...')

    iter_id = 0
    count = 0
    while True:
        print('Invoking', iter_id)

        message = {
            'iter_id': iter_id,
            'match_image_id': match_image_id
        }

        print('Sending message', json.dumps(message))
        response = s3_client.put_object(
            Bucket='cowhub-production-images',
            Key='match-metadata/%s-%s.metadata.json' % (match_image_id, iter_id),
            ACL='private',
            Body=json.dumps(message)
        )

        count += 1

        print('Invocation', iter_id, 'success.')

        iter_id, _ = REDIS_CONN.scan(cursor=iter_id, match=MATCH, count=os.environ['LAMBDA_COUNT'])
        if iter_id == 0:
            break

    r = requests.post(
        'http://api.cowhub.co.uk/match/%s/lambda/count' % match_image_id,
        data={'count': count})
    try_count = 1
    while try_count < 5 and not r.status_code is 200:
        r = requests.post(
            'http://api.cowhub.co.uk/match/%s/lambda/count' % match_image_id,
            data={'count': count})

    return {
        'status': 'success' if r.status_code is 200 else 'failed'
    }


def compare_handler(event, context):
    s3_info = event['Records'][0]['s3']
    s3_bucket = s3_info['bucket']['name']
    s3_key = s3_info['object']['key']

    print('Metadata put:', s3_bucket, s3_key)
    print('Retrieving metadata from S3')
    prt(context)

    print('Retrieved metadata from S3')
    prt(context)

    metadata = s3_key.split('/')[-1].split('.')[0].split('-')
    match_image_id, iter_id = metadata

    print('Match Image ID:', match_image_id)
    print('Iteration  ID:', iter_id)
    prt(context)

    print('Retrieving match descriptor')
    prt(context)

    match_item = REDIS_CONN.get('match_image_id_%s' % (match_image_id))
    match_image_descriptor = kp_loads(match_item)

    print('Retrieved and processed match descriptor')
    print('Retrieving potential match descriptors from Redis')
    prt(context)

    _, matches = REDIS_CONN.scan(cursor=iter_id, match=MATCH, count=os.environ['LAMBDA_COUNT'])

    print('Retrieved matches, starting iteration')
    prt(context)

    best_value = float('inf')
    best_match = None
    for match in matches:
        print('Processing match:', match)
        prt(context)

        match_descriptor = REDIS_CONN.get(match)
        descriptor = kp_loads(match_descriptor)

        print('Match loaded:', match)
        prt(context)

        diff = calc_diff(match_image_descriptor[1], descriptor[1])
        if diff < best_value:
            print('Match is improvement!')
            prt(context)
            best_value = diff
            best_match = match.split('_')[-1]

    print('Generated best match')
    prt(context)

    r = requests.post(
        'http://api.cowhub.co.uk/match/%s/lambda' % match_image_id,
        data={'count': count})
    try_count = 1
    while try_count < 5 and not r.status_code is 200:
        r = requests.post(
            'http://api.cowhub.co.uk/match/%s/lambda/count' % match_image_id,
            data={
                "image_id": best_match,
                "value": best_value
            })

    return {
        'status': 'success' if r.status_code is 200 else 'failed'
    }
