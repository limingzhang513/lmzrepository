# -*- coding:utf-8 -*-

from fdfs_client.client import Fdfs_client, ConnectionPool
from . import fdfs_tracker


class RedisError(Exception):
    """
    错误信息
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class FastClient(Fdfs_client):
    """
    链接池
    """

    def __init__(self):
        self.tracker_pool = ConnectionPool(**fdfs_tracker)
        self.timeout = fdfs_tracker['timeout']

    def __del__(self):
        try:
            self.pool.destroy()
            self.pool = None
        except:
            pass
