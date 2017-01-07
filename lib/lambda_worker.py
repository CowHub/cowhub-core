import pickle
import boto3
from functools import reduce
from redis import StrictRedis
# import elasticache_auto_discovery
import os
import json

from worker import calc_diff, generate_descriptor


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


def register_handler(event, context):
    s3_info = event['Records'][0]['s3']
    s3_bucket = s3_info['bucket']['name']
    s3_key = s3_info['object']['key']

    print 'Image put:', s3_bucket, s3_key

    image_id = s3_key.split('/')[-1].split('-')[0]

    print 'Image ID:', image_id
    print 'Retrieving image from S3'

    s3_client = boto3.client('s3')
    image = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)['Body']

    print 'Retrieved image from S3'
    print 'Generating image desriptor'

    image_descriptor = generate_descriptor(image)

    print 'Generated image descriptor. Sending to Redis.'

    REDIS_CONN.set('cattle_image_id_%s' % (image_id, ), pickle.dumps(image_descriptor))

    print 'Sent to Redis successfully.'

    return {
        'status': 'success'
    }


def match_handler(event, _):
    iter_id = event['iter_id']
    image = event['image']
    image_descriptor = generate_descriptor(image)

    _, keys = REDIS_CONN.scan(cursor=iter_id, match=MATCH, count=LAMBDA_COUNT)

    def reducer((a_id, v), b_id):
        i = pickle.loads(REDIS_CONN.get(b_id))
        diff = calc_diff(image_descriptor, i)

        if diff < v:
            return b_id, diff
        else:
            return a_id, v

    image_id, value = reduce(reducer, keys, (None, float("inf")))

    return {
        'image_id': image_id,
        'value': value
    }
