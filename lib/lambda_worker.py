import boto3
import pickle
from functools import reduce
from rediscluster import StrictRedisCluster
import elasticache_auto_discovery

from worker import calc_diff

client = boto3.client('lambda')
elastic_ip = ''  # TODO: fill in
elastic_port = ''
elastic_endpoint = '%s:%s' % (elastic_ip, elastic_port)
nodes = elasticache_auto_discovery.discover(elastic_endpoint)
nodes = map(lambda x: {'host': x[1], 'port': x[2]}, nodes)
redis_conn = StrictRedisCluster(elastic_ip, elastic_port)

MATCH = 'cattle_image_id_*'
LAMBDA_COUNT = 25


def handler(event, context):
    iter_id = event['iter_id']
    image = event['image']
    image_descriptor = pickle.loads(image)

    _, keys = redis_conn.scan(cursor=iter_id, match=MATCH, count=LAMBDA_COUNT)

    def reducer((a_id, v), b_id):
        i = pickle.loads(redis_conn.get(b_id))
        diff = calc_diff(image_descriptor, i)

        if diff < v:
            return b_id, diff
        else:
            return a_id, v

    image_id, value = reduce(reducer,
                             keys,
                             (None, float("inf"))
                             )

    return {
        'image_id': image_id,
        'value': value
    }
