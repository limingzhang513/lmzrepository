# -*- coding:utf-8 -*-
import pika
from flask import json
from img_detection_recognition import image_recognition, image_detection

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# 声明队列
channel.queue_declare(queue='preprocessing_queue')


def preprocessing(n):
    n = json.loads(n)

    print('get_data')

    if n[1] == 1:
        return image_recognition(n)
    elif n[1] == 2:
        return image_detection(n)

    # return 'ok'


def on_request(ch, method, props, body):
    n = body

    response = preprocessing(n)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id= \
                                                         props.correlation_id),
                     body=response)
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    channel.basic_qos(prefetch_count=1)  # 设置最大接收消息数值
    # 要接受信息的队列和要处理信息得到函数
    channel.basic_consume(on_request, queue='preprocessing_queue')
    print(" [x] Awaiting RPC requests")

    channel.start_consuming()
