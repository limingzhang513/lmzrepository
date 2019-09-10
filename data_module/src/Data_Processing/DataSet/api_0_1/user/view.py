# -*- coding:utf-8 -*-
from flask import request, jsonify, session, current_app, g
from DataSet.models.userModel import User
from DataSet.token.auths import auth
from DataSet.utils import commons
from DataSet.utils.auth_decorator import user_required
from DataSet.utils.serial_code import RET
from DataSet.api_0_1.user import api


@api.route('/api/users', methods=['POST'])
def new_user():
    """
    注册
    :return:
    """
    user_data = request.get_json()
    if not user_data:
        return jsonify(err_no=RET.PARAMERR, err_desc='参数错误')
    user_name = user_data.get('user_name')
    password = user_data.get('password')
    email = user_data.get('email')
    if not all([user_name, password]):
        return jsonify(err_no=RET.PARAMERR, err_desc='参数不完整')
    if User.query.filter_by(name=user_name).first():
        return jsonify(err_no=RET.PARAMERR, err_desc='用户已经存在')
    user = User(email=email, name=user_name)
    user.password = password
    user.add(user)
    if user.id:
        returnUser = {
            'id': user.id,
            'username': user.name,
            'email': user.email,
            'login_time': user.login_time
        }
        return jsonify(commons.trueReturn(returnUser, "用户注册成功"))
    else:
        return jsonify(commons.falseReturn(RET.DATAERR, '', '用户注册失败'))


@api.route('/login', methods=['POST'])
def login():
    """
    登陆
    :return:
    """
    # current_app.logger.info('[login] req received')
    user_data = request.get_json()
    if not user_data:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '参数错误'))
    user_name = user_data.get('user_name')
    password = user_data.get('password')
    if not all([user_name, password]):
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '用户名和密码不能为空'))
    # current_app.logger.info('[login] sql start')
    try:
        user = User.query.filter_by(name=user_name).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(commons.falseReturn(RET.DBERR, '', '查询数据库异常'))
    # current_app.logger.info('[login] sql finished')
    if user is None or not user.check_password(password):
        return jsonify(commons.falseReturn(RET.DATAERR, '', '用户名或密码错误'))
    # current_app.logger.info('[login] returning')
    return auth.authenticate(user_name, password)


@api.route('/user', methods=['GET'])
@user_required
def get():
    """
    获取用户信息
    :return: json
    """
    result = auth.identify(request)
    if 0 == result['err_no'] and result['data']:
        user = User.get(result['data'])
        returnUser = {
            'id': user.id,
            'username': user.name,
            'email': user.email,
            'login_time': user.login_time
        }
        result = commons.trueReturn(returnUser, "请求成功")
    return jsonify(result)


@api.route('/logout', methods=['GET'])
def logout():
    """
    退出
    :return:
    """
    csrf_token = session.get('csrf_token')
    session.clear()
    session['csrf_token'] = csrf_token
    return jsonify(err_no=RET.OK, err_desc='OK')





