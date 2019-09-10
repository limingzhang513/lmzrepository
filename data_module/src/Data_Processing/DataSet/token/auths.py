# -*- coding:utf-8 -*-
import jwt
import datetime
import time
from flask import current_app, jsonify, g
from DataSet.models import User
from DataSet.utils.serial_code import RET
from DataSet.utils import commons

import logging


class Auth():
    @staticmethod
    def encode_auth_token(user_id, login_time):
        """
        生成认证Token
        :param user_id: int
        :param login_time: int(timestamp)
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=10),
                'iat': datetime.datetime.utcnow(),
                'iss': 'ken',
                'data': {
                    'id': user_id,
                    'login_time': login_time
                }
            }
            return jwt.encode(
                payload,
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        验证Token
        :param auth_token:
        :return: integer|string
        """
        try:
            # payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'), leeway=datetime.timedelta(seconds=10))
            # 取消过期时间验证
            # logging.info( "auth token %s"%(auth_token) )
            payload = jwt.decode(auth_token, current_app.config['SECRET_KEY'], options={'verify_exp': False})
            if 'data' in payload and 'id' in payload['data']:
                return payload
            else:
                raise jwt.InvalidTokenError
        except jwt.ExpiredSignatureError:
            return 'Token过期'
        except jwt.InvalidTokenError:
            return '无效Token'

    def authenticate(self, username, password):
        """
        用户登录，登录成功返回token；登录失败返回失败原因
        :param password:
        :return: json
        """
        userInfo = User.query.filter_by(name=username).first()
        if userInfo is None:
            return jsonify(commons.falseReturn(RET.NODATA, '', '找不到用户'))
        else:
            if userInfo.check_password(password):
                login_time = int(time.time())
                userInfo.login_time = login_time
                userInfo.update()
                token = self.encode_auth_token(userInfo.id, login_time)
                return jsonify(commons.trueReturn(token.decode(), '登陆成功'))
            else:
                return jsonify(commons.falseReturn(RET.DBERR, '', '密码不正确'))

    def identify(self, request):
        """
        用户权鉴
        :return: list
        """
        auth_header = request.headers.get('Authorization')  # 请求头获得信息
        if auth_header:
            auth_tokenArr = auth_header.split(" ")
            if not auth_tokenArr or auth_tokenArr[0] != 'JWT' or len(auth_tokenArr) != 2:
                result = commons.falseReturn(RET.PARAMERR, '', '请传递正确的验证头信息')
            else:
                auth_token = auth_tokenArr[1]
                payload = self.decode_auth_token(auth_token)  # 验证token
                if not isinstance(payload, str):  # 判断payload是否为str类型
                    user = User.get(payload['data']['id'])
                    if user is None:
                        result = commons.falseReturn(RET.DATAERR, '', '找不到该用户信息')
                    else:
                        if user.login_time == payload['data']['login_time']:
                            g.user = user  # 设置每个请求 g 保存的对象
                            result = commons.trueReturn(user.id, '请求成功')
                        else:
                            result = commons.falseReturn(RET.DATAERR, '', 'Token已更改，请重新登录获取')
                else:
                    result = commons.falseReturn(RET.DATAERR, '', payload)
        else:
            result = commons.falseReturn(RET.NODATA, '', '没有提供认证token')
        return result


auth = Auth()
