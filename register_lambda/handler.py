from __future__ import print_function

import json
import urllib
import boto3
from worker import generate_descriptor

s3 = boto3.client('s3')
cache = boto3.client('elasticache')
libdir = os.path.join(os.getcwd(), 'local', 'lib')

def lambda_handler(event, context):
    key, image = get_image(event)
    cattle_id = key
    descriptor = generate_descriptor(image)
    response = store_decriptor(descriptor, cattle_id)
    return response

def get_image(event):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        return key, response['Body']
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}.'.format(key, bucket))
        raise e

def store_decriptor(descriptor, cattle_id):
    try:
        response = client.add_tags_to_resource(
            ResourceName='string', # TODO: insert correct ARN
            Tags=[
                {
                    'Key': 'cattle_descriptor_' + cattle_id,
                    'Value': descriptor
                },
            ]
        )
        return response
    except Exception as e:
        print(e)
        print('Error storing descriptor {} for cattle {} in elasticache.'.format(descriptor, cattle_id))
        raise e
