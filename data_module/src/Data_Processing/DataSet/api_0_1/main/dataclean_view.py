# -*- coding:utf-8 -*-
import base64
import time
from flask import json, current_app, jsonify, g, request
from DataSet import db, redis_store
from DataSet.api_0_1.main import _main
from DataSet.models import Collection, Label, User, Share
from DataSet.token.auths import auth
from DataSet.utils import commons
from DataSet.utils.auth_decorator import user_required, user_identification
from DataSet.utils.serial_code import RET


@_main.route('/data_clean/cluster/<int:collection_id>', methods=['POST'])
@user_required
def Cluster(collection_id):
    """
    聚类
    :return:
    """
    local_time = time.time()
    collection = user_identification(collection_id, g.user.id)  # 要聚类的数据集
    if not collection:
        return jsonify(commons.falseReturn(RET.DBERR, '', '不存在的数据集'))
    if 1 != collection.type:
        return jsonify(commons.falseReturn(RET.DATAERR, '', '请选择正确的数据集类型'))
    collection
    pass
