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
    request_id = key
    potential_matches = get_all_desciptor()
    match = find_match(image, potential_matches)
    response = store_decriptor(request_id, match)
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

def get_all_desciptor():
    try:
        response = client.list_tags_for_resource(
            ResourceName='string', # TODO: insert correct ARN
        )
        return response['TagList']
    except Exception as e:
        print(e)
        print('Error retrieving all descriptor from in elasticache.')
        raise e

def store_match(request_id, match_id):
    # TODO: write method to connect to RDS and store result
