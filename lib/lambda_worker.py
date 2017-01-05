import boto3

client = boto3.client('lambda')
elastic_end_point = ''
elastic_port = ''


def handler(event, context):
    image = event['image']
    batch = event['batch']
    return None
