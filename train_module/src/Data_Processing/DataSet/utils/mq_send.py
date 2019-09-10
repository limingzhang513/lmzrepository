# !/usr/bin/python2
'''
    train task queue sender
'''

import pika
import json


def train_task_send(data):
    """
    put the train task into rabbitMQ queue
    :param data: parameter
    :return:
    """
    parameters = pika.ConnectionParameters(host='localhost',
                                           heartbeat_interval=0)
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()
    channel.queue_declare(queue='train_queue', durable=True)
    channel.basic_qos(prefetch_count=1)
    body = json.dumps(data)

    channel.basic_publish(exchange='',
                          routing_key='train_queue',
                          body=body,
                          properties=pika.BasicProperties(
                              delivery_mode=2,
                          )
                          )
    connection.close()
