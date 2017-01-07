import pickle
import boto3
from functools import reduce
from redis import StrictRedis
# import elasticache_auto_discovery
import os
import json

from worker import read_base64, calc_diff, generate_descriptor


def get_redis():
    elastic_ip = os.environ['ELASTICACHE_IP']
    elastic_port = os.getenv('ELASTICACHE_PORT', '6379')

    print 'Connecting to Redis at:', elastic_ip, elastic_port

    elastic_endpoint = '%s:%s' % (elastic_ip, elastic_port)
    # nodes = elasticache_auto_discovery.discover(elastic_endpoint)
    # nodes = map(lambda x: {'host': x[1], 'port': x[2]}, nodes)
    redis_conn = StrictRedis(elastic_endpoint)

    print 'Connected to Redis.'

    return redis_conn


REDIS_CONN = get_redis()

MATCH = 'cattle_image_id_*'
LAMBDA_COUNT = 25


def send_descriptor_to_redis(event, prefix):
    s3_info = event['Records'][0]['s3']
    s3_bucket = s3_info['bucket']['name']
    s3_key = s3_info['object']['key']

    print 'Image put:', s3_bucket, s3_key
    print 'Retrieving image from S3'

    s3_client = boto3.client('s3')
    image = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)['Body'].read()

    print 'Retrieved image from S3'

    id_ = s3_key.split('/')[-1].split('-')[0]

    print 'Event ID:', id_
    print 'Generating image desriptor'

    image_array = read_base64(image)
    image_descriptor = generate_descriptor(image_array)

    print 'Generated image descriptor. Sending to Redis.'

    REDIS_CONN.set('%s%s' % (prefix, id_), pickle.dumps(image_descriptor))

    print 'Sent to Redis successfully.'


def register_handler(event, context):
    send_descriptor_to_redis(event, 'cattle_image_id_')
    return { 'status': 'success' }


def match_handler(event, context):
    send_descriptor_to_redis(event, 'match_image_id_')
    return { 'status': 'success' }


# def compare_handler(event, context):
#     key, image = get_image_from_s3(event)
#
#     iter_id = event['iter_id']
#     image = event['image']
#     image_descriptor = generate_descriptor(image)
#
#     _, keys = REDIS_CONN.scan(cursor=iter_id, match=MATCH, count=LAMBDA_COUNT)
#
#     def reducer((a_id, v), b_id):
#         i = pickle.loads(REDIS_CONN.get(b_id))
#         diff = calc_diff(image_descriptor, i)
#
#         if diff < v:
#             return b_id, diff
#         else:
#             return a_id, v
#
#     image_id, value = reduce(reducer, keys, (None, float("inf")))
#
#     return {
#         'image_id': image_id,
#         'value': value
#     }
