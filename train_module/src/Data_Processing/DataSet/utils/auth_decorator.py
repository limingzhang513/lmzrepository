# -*- coding:utf-8 -*-

from functools import wraps
from flask import jsonify, request
from DataSet.utils.serial_code import RET
from DataSet.token.auths import auth


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        result = auth.identify(request)
        if 0 == result['err_no'] and result['data']:
            return f(*args, **kwargs)
        else:
            return jsonify(err_no=RET.SESSIONERR, err_desc=result['err_desc'])
    return wrapper
