from __future__ import print_function

import json
import urllib
import boto3
import pickle
import sys

from diff import calc_diff, get_descriptor
from crop import crop

s3 = boto3.client('s3')
cache = boto3.client('elasticache')
rds = boto3.client('rds')

def lambda_handler(event, context):
    request_id = 42 # TODO: get request_id from event / context
    image = get_image(event)
    descriptor = generate_descriptor(image)
    match_id = find_match(descriptor)
    store_match(request_id, match_id)

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

def find_match(descriptor):
    diff = sys.maxint
    for potential_match in get_all_desciptor()
        d = calc_diff(descriptor, pickle.load(potential_match['Value']))
        if (d < diff)
            diff = d
            match = potential_match['Key']
    return match[18:]

def store_match(request_id, match_id):
    # TODO: write method to connect to RDS and store result
