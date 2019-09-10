# -*- coding:utf-8 -*-
import pika
from pHash import clean
from flask import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# 声明队列
channel.queue_declare(queue='same_images_clean_queue')

def preprocessing_clean(n):
    n = json.loads(n)
    # print(n)
    # print(type(n))
    # a = list()
    # n = n.split(', ')
    print("get date")
    # for i in n:
    #     i = i.encode('utf-8')
    #     i = str(i).replace("'",'')
    #     print(type(i))
    #     a.append(i)
    # print(a)
    return clean(n)
    # return 'ok'

def on_request(ch, method, props, body):
    n = body

    response = preprocessing_clean(n)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id= \
                                                     props.correlation_id),
                     body=response)
    ch.basic_ack(delivery_tag= method.delivery_tag)

if __name__ == '__main__':

    channel.basic_qos(prefetch_count=1)
    # 要接受信息的队列和要处理信息得到函数
    channel.basic_consume(on_request, queue='same_images_clean_queue')
    print(" [x] Awaiting RPC requests")

    channel.start_consuming()