import cPickle as pickle
import numpy
import cv2
from redis import StrictRedis
import boto3
from worker import read_base64, generate_descriptor


def kp_dumps(descriptor):
    kps, mt = descriptor
    index = numpy.empty(len(kps), dtype=tuple)
    for (i, kp) in enumerate(kps):
        index[i] = (kp.pt, kp.size, kp.angle, kp.response, kp.octave, kp.class_id)
    return pickle.dumps((index, mt))


def kp_loads(string):
    (index, mt) = pickle.loads(string)
    array = numpy.empty(index.shape, dtype=object)
    for i in range(0, len(array)):
        t = index[i]
        array[i] = cv2.KeyPoint(t[0][0], t[0][1], _size=t[1], _angle=t[2], _response=t[3], _octave=t[4], _class_id=t[5])
    return array.tolist(), mt


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


def get_descriptor_from_event(event, context, REDIS_CONN, prefix=None):
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
