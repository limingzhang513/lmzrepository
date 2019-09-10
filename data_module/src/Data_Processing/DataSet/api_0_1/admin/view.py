# -*- coding:utf-8 -*-
from flask import request, jsonify

from DataSet import db
from DataSet.models import Role, User
from DataSet.utils import commons
from DataSet.utils.auth_decorator import admin_required
from DataSet.utils.serial_code import RET
from . import _admin


@_admin.route('/admin/auth/add', methods=['POST'])
@admin_required
def add_auth():
    """权限增加"""
    data = request.get_json()  # 获取请求的json数据
    user_id = data.get('id')
    if not user_id:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '用户id不能为空'))
    users = User.query.filter_by(id=user_id).first()  # 数据库匹配第一条数据
    if users is None:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '没有此用户'))
    role = users.role.permissions + 2  # 查出用户现在的权限，给用户增加权限
    if role not in [1, 3, 7]:
        return jsonify(commons.falseReturn(RET.AUTHERR, '', '未知权限'))
    users.role = Role.query.filter_by(permissions=role).first()
    db.session.add(users)  # 保存数据库
    db.session.commit()  # 提交到数据库
    return jsonify(commons.trueReturn('已升级为普通用户', 'OK'))


@_admin.route('/admin/auth/remove', methods=['POST'])
@admin_required
def remove_auth():
    """权限删除"""
    data = request.get_json()
    user_id = data.get('id')
    if not user_id:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '用户id不能为空'))
    users = User.query.filter_by(id=user_id).first()
    if users is None:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '没有此用户'))
    role = users.role.permissions - 2
    if role not in [1, 3, 7]:
        return jsonify(commons.falseReturn(RET.AUTHERR, '', '未知权限'))
    users.role = Role.query.filter_by(permissions=role).first()
    db.session.add(users)
    db.session.commit()
    return jsonify(commons.trueReturn('以降级为标注用户', 'OK'))

