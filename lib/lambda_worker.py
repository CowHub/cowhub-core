from __future__ import print_function
from utils import get_descriptor_from_event, kp_loads, prt, get_redis
import os
import json
import requests

from worker import calc_diff, generate_descriptor


REDIS_CONN = get_redis()
MATCH = 'cattle_image_id_*'


def register_handler(event, context):
    get_descriptor_from_event(event, context, REDIS_CONN, prefix='cattle_image_id_')
    return {'status': 'success'}


def register_delete_handler(event, context):
    s3_info = event['Records'][0]['s3']
    s3_bucket = s3_info['bucket']['name']
    s3_key = s3_info['object']['key']

    id_ = s3_key.split('/')[-1].split('-')[0]

    REDIS_CONN.delete('cattle_image_id_%s' % (id_))


def match_handler(event, context):
    match_image_id, match_image_descriptor, s3_client = get_descriptor_from_event(event, context, REDIS_CONN, prefix='match_image_id_')

    print('Invoking lambda comparisons...')

    iter_id = 0
    iter_count = 0
    while True:
        print('Invoking', iter_id)
        prt(context)

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

        iter_count += 1

        print('Invocation', iter_id, 'success.')
        prt(context)

        iter_id, _ = REDIS_CONN.scan(cursor=iter_id, match=MATCH, count=os.environ['LAMBDA_COUNT'])
        if iter_id == 0:
            break

    print('Sending request to API')
    prt(context)
    r = requests.post(
        'http://%s/cattle/match/%s/lambda/count' % (os.environ['API_IP_ADDRESS'], match_image_id),
        data={'count': iter_count})

    print('Sent request')
    prt(context)

    return {
        'success': r.status_code is 200,
        'response': {
            'content': r.content,
            'status_code': r.status_code,
            'text': r.text
        }
    }


def match_delete_handler(event, context):
    s3_info = event['Records'][0]['s3']
    s3_bucket = s3_info['bucket']['name']
    s3_key = s3_info['object']['key']

    metadata = s3_key.split('/')[-1].split('.')[0].split('-')
    match_image_id, iter_id = metadata

    REDIS_CONN.delete('match_image_id_%s' % (match_image_id))


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

    print('Sending request to API')
    prt(context)
    r = requests.post(
        'http://%s/cattle/match/%s/lambda' % (os.environ['API_IP_ADDRESS'], match_image_id),
        data={
            "image_id": best_match,
            "value": best_value
        })

    print('Sent request')
    prt(context)

    return {
        'success': r.status_code is 200,
        'response': {
            'content': r.content,
            'status_code': r.status_code,
            'text': r.text
        }
    }
