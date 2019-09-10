# !/usr/bin/python2
# -*- coding:utf-8 -*-

import functools
from flask import session, jsonify, g
from DataSet.utils.serial_code import RET


class RegexConverter(BaseException):
    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        self.regex = args[0]


def login_request(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id')
        if user_id is None:
            return jsonify(err_no=RET.SESSIONERR, err_desc='用户未登陆')
        else:
            g.user_id = user_id
            return f(*args, **kwargs)
    return wrapper


def trueReturn(data, err_desc):
    return {
        "err_no": 0,
        "data": data,
        "err_desc": err_desc
    }


def falseReturn(err_no, data, err_desc):
    return {
        "err_no": err_no,
        "data": data,
        "err_desc": err_desc
    }
