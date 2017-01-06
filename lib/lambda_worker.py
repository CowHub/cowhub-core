import boto3
import pickle
from functools import reduce
from rediscluster import StrictRedisCluster
import elasticache_auto_discovery
import os

from worker import calc_diff, generate_descriptor


def get_redis():
    elastic_ip = os.environ['ELASTIC_IP']
    elastic_port = os.getenv('ELASTIC_PORT', '6379')
    elastic_endpoint = '%s:%s' % (elastic_ip, elastic_port)
    nodes = elasticache_auto_discovery.discover(elastic_endpoint)
    nodes = map(lambda x: {'host': x[1], 'port': x[2]}, nodes)
    redis_conn = StrictRedisCluster(nodes)

    return redis_conn


REDIS_CONN = get_redis()

MATCH = 'cattle_image_id_*'
LAMBDA_COUNT = 25


def register_handler(event, _):
    image = event['image']
    image_id = event['image_id']
    image_descriptor = generate_descriptor(image)

    REDIS_CONN.set('cattle_image_id_%s' % (image_id,), pickle.dumps(image_descriptor))

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
