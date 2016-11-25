import pika
import os
import json

from .worker import Worker

HOST = os.environ['RABBIT_HOST']
PORT = os.environ['RABBIT_PORT']
QUEUE = 'task_queue'

WORKER = Worker()


def callback(ch, method, props, body):
    body_data = json.loads(body)
    mode = body_data['mode']

    if mode == 'register':
        params = tuple(body_data[x] for x in ['cattle_id', 'image'])
        WORKER.start_processing(*params)
    elif mode == 'match':
        params = tuple(body_data[x] for x in ['image', 'server_id', 'request_id'])
        WORKER.start_matching(*params)

    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE, durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue=QUEUE)

    channel.start_consuming()
