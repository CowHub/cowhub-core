import pika
import os

HOST = os.environ['RABBIT_HOST']
QUEUE = 'task_queue'

connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST))
channel = connection.channel()

channel.queue_declare(queue=QUEUE, durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')


def callback(ch, method, properties, body):
    # TODO: Add consumer method
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=QUEUE)

channel.start_consuming()
