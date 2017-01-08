from __future__ import print_function
from utils import kp_dumps, kp_loads
import boto3
from redis import StrictRedis
import os
import json

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
LAMBDA_COUNT = 25


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

    return id_, image_descriptor


def register_handler(event, context):
    get_descriptor_from_event(event, context, prefix='cattle_image_id_')
    return {'status': 'success'}


def match_handler(event, context):
    match_image_id, match_image_descriptor = get_descriptor_from_event(event, context)

    aws_lambda = boto3.client('lambda')
    iter_id = 0
    while 1:
        aws_lambda.invoke(
            FunctionName='cowhub-image-compare',
            InvocationType='Event',
            Payload=json.dumps({
                'iter_id': iter_id,
                'match_image_id': match_image_id,
                'match_image_descriptor': match_image_descriptor
            })
        )

        iter_id, _ = REDIS_CONN.scan(cursor=iter_id, match=MATCH, count=LAMBDA_COUNT)
        if iter_id == 0:
            break

    return {'status': 'success'}


def compare_handler(event, context):
    pass
