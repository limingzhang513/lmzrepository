# -*- coding:utf-8 -*-
import pika
from flask import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# 声明队列
channel.queue_declare(queue='create_version_queue')

def version(n):
    n = json.loads(n)
    print ('get_data')
    path_name = '%s-%s.zip' % (n[0], n[1])
    return path_name

def on_request(ch, method, props, body):
    n = body

    response = version(n)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id= \
                                                     props.correlation_id),
                     body=response)
    ch.basic_ack(delivery_tag= method.delivery_tag)

if __name__ == '__main__':

    channel.basic_qos(prefetch_count=1)
    # 要接受信息的队列和要处理信息得到函数
    channel.basic_consume(on_request, queue='create_version_queue')
    print(" [x] Awaiting RPC requests")

    channel.start_consuming()