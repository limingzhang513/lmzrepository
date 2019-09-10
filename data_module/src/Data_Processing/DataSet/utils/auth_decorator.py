# -*- coding:utf-8 -*-

import functools

from DataSet.models.roleModel import Permission
from DataSet.token.auths import auth
from DataSet.utils.serial_code import RET
from flask import jsonify, current_app, request, g
from DataSet.models import Collection, User


def permission_required(permission):
    """权限装饰器"""

    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            result = auth.identify(request)
            if 0 == result['err_no'] and result['data']:
                user = User.get(result['data'])
                if not user.can(permission):
                    return jsonify(err_no=RET.AUTHERR, err_desc='权限不足')
            else:
                return jsonify(result)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):  # 管理员权限装饰器
    """管理员"""
    return permission_required(Permission.ADMINISTER)(f)


def user_required(f):  # 普通用户权限装饰器
    """普通用户"""
    return permission_required(Permission.CRUD)(f)


def user_identification(collection_id, user_id=None):
    """用户鉴定"""
    try:
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return None
    except AttributeError as e:
        current_app.logger.error(e)
        return None
    collection = Collection.query.filter_by(user_id=user_id, id=collection_id).first()
    collections = (user.share.share_collection if user.share.share_collection else '[]')  # 一对一查询Share表

    try:
        if not collection and collection_id not in eval(collections):
            return None
    except AttributeError as e:
        current_app.logger.error(e)
        return None
    collection = Collection.query.filter_by(id=collection_id).first()  # 当前集合
    return collection
