# -*- coding:utf-8 -*-
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# 声明队列
channel.queue_declare(queue='delete_set_queue')


def delete(n):
    # n = json.loads(n)
    print('get_data')
    return n
    # return 'ok'


def on_request(ch, method, props, body):
    n = body

    response = delete(n)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=response)
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    channel.basic_qos(prefetch_count=1)
    # 要接受信息的队列和要处理信息得到函数
    channel.basic_consume(on_request, queue='delete_set_queue')
    print(" [x] Awaiting RPC requests")

    channel.start_consuming()
