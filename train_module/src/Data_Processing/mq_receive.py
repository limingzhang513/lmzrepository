# !/usr/bin/python2
'''
    train task queue receiver
'''

import pika
import json
from DataSet.utils.train_req import dl_req


hostname = 'localhost'
parameters = pika.ConnectionParameters(host=hostname,
                                       heartbeat_interval=0)
connection = pika.BlockingConnection(parameters)

channel = connection.channel()
channel.queue_declare(queue='train_queue', durable=True)


def callback(ch, method, properties, body):
    if body is not None and body != 0:
        print("[x] Received %r" % (json.loads(body)))
        print 'Send train request'
        dl_req(body)
    else:
        print 'task par is blank'
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue='train_queue')
print ' [*] Waiting for messages. To exit press CTRL+C'
channel.start_consuming()




