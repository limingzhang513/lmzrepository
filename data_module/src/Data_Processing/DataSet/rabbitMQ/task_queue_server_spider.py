# -*- coding:utf-8 -*-
import pika
from clawer import Crawler
from flask import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# 声明队列
channel.queue_declare(queue='spider_queue')

def spider(n):
    n = json.loads(n)
    print(n)
    crawler = Crawler(0.05)
    spider_imgdict = crawler.start(n['keyword'], n['spider_page_num'], n['start_page'], n['number'])
    print(spider_imgdict)
    # spider_imglist = [u'http://pic.58pic.com/58pic/16/19/43/05v58PIC9VU_1024.jpg', u'http://fx120.120askimages.com/120ask_news/2017/0525/201705251495676599321328.jpg', u'http://pic.90sjimg.com/back_pic/qk/back_origin_pic/00/02/28/fefc34394a823bc1188756d64b3961aa.jpg', u'http://pic28.photophoto.cn/20130813/0008020214685777_b.jpg']
    spider_imglist = json.dumps(spider_imgdict)
    return spider_imglist
    # return 'ok'

def on_request(ch, method, props, body):
    n = body

    response = spider(n)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id= \
                                                     props.correlation_id),
                     body=response)
    ch.basic_ack(delivery_tag= method.delivery_tag)

if __name__ == '__main__':

    channel.basic_qos(prefetch_count=1)
    # 要接受信息的队列和要处理信息得到函数
    channel.basic_consume(on_request, queue='spider_queue')
    print(" [x] Awaiting RPC requests")

    channel.start_consuming()