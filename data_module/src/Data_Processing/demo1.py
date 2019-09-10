# -*- coding: utf-8 -*-

"""
实用功能。
"""

import datetime
import decimal
import time


def model_to_dict(model):
    """将sqlalchemy model对象转化为dict。"""
    if model is None:
        return None
    ret = dict()
    for attr in dir(model):
        value = getattr(model, attr)
        if attr.startswith('_'):
            continue
        elif value is None:
            continue
        elif attr in ('metadata', 'query'):
            continue
        elif isinstance(value, (datetime.date, datetime.datetime)):
            value = value.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(value, decimal.Decimal):
            value = float(value)
        ret[attr] = value
    return ret


def datetime_to_timestamp(dt):
    """将datetime对象转换为以毫秒为单位的时间戳。"""
    # TODO: @wanglanwei: 转换有误差。
    ms = dt.microsecond
    timetuple = dt.timetuple()
    timestamp = time.mktime(timetuple)
    timestamp = int(timestamp) * 1000 + ms
    return timestamp


def timestamp_to_datetime(timestamp):
    """将以毫秒为单位的时间戳timestamp转换为datetime对象。"""
    return datetime.datetime.fromtimestamp(timestamp / 1000).replace(microsecond=timestamp % 1000)

