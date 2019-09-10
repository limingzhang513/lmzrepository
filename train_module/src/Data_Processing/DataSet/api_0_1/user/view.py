# !/usr/bin/python2
# -*- coding:utf-8 -*-

import requests
from .. import api
from flask import request, jsonify, current_app
from DataSet.utils.serial_code import RET
from DataSet.utils import commons

import json


@api.route('/login', methods=['POST'])
def login():
    """
    登陆
    :return:
    """
    user_data = request.get_json()
    if not user_data:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '参数错误'))
    user_name = user_data.get('user_name')
    password = user_data.get('password')
    if not all([user_name, password]):
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '用户名和密码不能为空'))
    payload = {'user_name': user_name, 'password': password}
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url=current_app.config['GET_TOKEN_URL'], headers=headers, data=json.dumps(payload))
    return r.text



