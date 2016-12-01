from __future__ import print_function

import json
import urllib
import boto3
import pickle

from diff import get_descriptor
from crop import crop

s3 = boto3.client('s3')
cache = boto3.client('elasticache')

def lambda_handler(event, context):
    cattle_id = 42 # TODO: get cattle_id from event / context
    image = get_image(event)
    descriptor = generate_descriptor(image)
    store_decriptor(descriptor, cattle_id)

def get_image(event):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return response['Body']
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}.'.format(key, bucket))
        raise e

def read_base64(b64_string):
    sbuf = StringIO()
    sbuf.write(base64.b64decode(b64_string))
    pimg = Image.open(sbuf)
    return cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)

def generate_descriptor(encodedImage):
    image = read_base64(encodedImage)
    (_, edge, _) = crop(image)
    return get_descriptor(edge)

def store_decriptor(descriptor, cattle_id):
    try:
        response = client.add_tags_to_resource(
            ResourceName='string', # TODO: insert correct ARN
            Tags=[
                {
                    'Key': 'cattle_descriptor_' + cattle_id,
                    'Value': pickle.dumps(descriptor)
                },
            ]
        )
        return response
    except Exception as e:
        print(e)
        print('Error storing descriptor {} for cattle {} in elasticache.'.format(descriptor, cattle_id))
        raise e
