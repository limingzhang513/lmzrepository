# !/usr/bin/python2
# -*- coding:utf-8 -*-

import jwt
import json
import requests
from flask import current_app, g
from DataSet.utils.serial_code import RET
from DataSet.utils import commons


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
            payload = jwt.decode(auth_token, current_app.config['SECRET_KEY'], options={'verify_exp': False})
            if 'data' in payload and 'id' in payload['data']:
                return payload
            else:
                raise jwt.InvalidTokenError
        except jwt.ExpiredSignatureError:
            return 'Token过期'
        except jwt.InvalidTokenError:
            return '无效Token'

    def identify(self, request):
        """
        用户权鉴
        :return: list
        """
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_tokenArr = auth_header.split(" ")
            if not auth_tokenArr or auth_tokenArr[0] != 'JWT' or len(auth_tokenArr) != 2:
                result = commons.falseReturn(RET.PARAMERR, '', '请传递正确的验证头信息')
            else:
                auth_token = auth_tokenArr[1]
                payload = self.decode_auth_token(auth_token)
                if not isinstance(payload, str):
                    headers = {'Authorization': auth_header}
                    r = requests.get(url=current_app.config['TOKEN_IDENTIFY_URL'], headers=headers)
                    try:
                        user_id = json.loads(r.text)['data']['id']
                    except Exception:
                        result = r.text
                        user_id = None
                    if user_id is None:
                        result = commons.falseReturn(RET.DATAERR, '', '找不到该用户信息')
                    else:
                        g.user_id = user_id
                        result = commons.trueReturn(user_id, '请求成功')
                else:
                    result = commons.falseReturn(RET.DATAERR, '', payload)
        else:
            result = commons.falseReturn(RET.NODATA, '', '没有提供认证token')
        return result


auth = Auth()
