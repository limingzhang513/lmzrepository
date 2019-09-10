# -*- coding:utf-8 -*-
import pika
import uuid
import time
from flask import json


class FibonacciRpcClient(object):
    """用户端"""

    def __init__(self):
        # 创建链接
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        self.channel = self.connection.channel()

        # 创建随机队列（并设置链接结束删除）
        result = self.channel.queue_declare(exclusive=True)
        # 获取队列名称
        self.callback_queue = result.method.queue
        # 指定接受服务端反馈信息的列表
        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    # 接收到返回数据的处理方法
    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n, routing_key):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',  # 交换器未使用
                                   routing_key=routing_key,  # 路由关键字锁定接收消息队列queue
                                   properties=pika.BasicProperties(
                                       reply_to=self.callback_queue,  # 回调的队列名，表示需要返回信息
                                       correlation_id=self.corr_id,  # 关联id
                                   ),
                                   body=n)  # 发布内容
        # 接收返回数据
        while self.response is None:
            self.connection.process_data_events()  # 未接收到执行超时等待
        return self.response  # 返回响应数据


# def create_file_task(user_id):
#     """默认生成文件"""
#     key = 'create_file_queue'
#     msg = '上传图片文件的参数'
#     # 创建用户端事例对象
#     fibonacci_rpc = FibonacciRpcClient()
#
#     print(" [create_file] Requesting ")
#     response = fibonacci_rpc.call(msg, key)
#     print(response)


def spider_task(spider_dict):
    """爬虫任务"""
    key = 'spider_queue'
    # 创建用户端事例对象
    fibonacci_rpc = FibonacciRpcClient()

    print(" [spider_task] Requesting ")
    spider_image_list = fibonacci_rpc.call(spider_dict, key)
    return spider_image_list


def same_images_clean_task(images_path_list):
    """图片去重处理任务"""
    key = 'same_images_clean_queue'
    fibonacci_rpc = FibonacciRpcClient()
    images_path_list = json.dumps(images_path_list)
    print(images_path_list)
    # 发送json数据开启队列
    print(" [same_images_clean_task] Requesting ")
    response_image_list = fibonacci_rpc.call(images_path_list, key)
    return response_image_list


def preprocessing_task(type_b64_list):
    key = 'preprocessing_queue'
    # 创建用户端事例对象
    fibonacci_rpc = FibonacciRpcClient()
    print(" [preprocessing_task] Requesting ")
    # 发送图片字节流
    json_data = fibonacci_rpc.call(json.dumps(type_b64_list), key)
    # print(" [preprocessing_task] return ", json_data)
    return json_data


def create_version_task(now_version_list):
    """创建合并版本"""
    key = 'create_version_queue'
    fibonacci_rpc = FibonacciRpcClient()
    now_version_list = json.dumps(now_version_list)
    print(" [create_version] Requesting ")
    path_name = fibonacci_rpc.call(now_version_list, key)
    return path_name


def delete_set_task(my_share):
    key = 'delete_set_queue'
    fibonacci_rpc = FibonacciRpcClient()
    print(" [delete_set] Requesting ")
    task_my_share = fibonacci_rpc.call(my_share, key)
    return task_my_share


def delete_version_task(label_url_path):
    """版本删除任务"""
    key = 'delete_version_queue'
    # 创建用户端事例对象
    fibonacci_rpc = FibonacciRpcClient()
    print(" [delete_version] Requesting ")
    response = fibonacci_rpc.call(label_url_path, key)
    return response


if __name__ == '__main__':
    print '程序开始时刻：', time.time()
    # 开启自调任务
    # s.enter(60, 2, preprocessing_quantitative_clean_task, ('image_quantitative', time.time()))
    # s.enter(1800, 2, preprocessing_timed_clean_task, ('image_timed', time.time()))
    # s.run()
