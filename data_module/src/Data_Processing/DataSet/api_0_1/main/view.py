# -*- coding:utf-8 -*-
import time

import cStringIO
from flask import current_app, jsonify, g, request
from flask import json
from flask import session

from DataSet import db, redis_store
from DataSet.api_0_1.main import _main
from DataSet.models import Collection, Label, User
from DataSet.models import Image
from DataSet.utils.change_json_file import cjf
from DataSet.utils.auth_decorator import user_required
from DataSet.token.auths import auth
from DataSet.utils.create_label_file import clf, image_size
from DataSet.utils.serial_code import RET
from DataSet.fastdfs.view import fun


@_main.route('/api/users/<int:id>', methods=['POST'])
def get_user(id):
    user = User.query.get(id)
    from PIL import Image
    path = request.files.getlist('upload_image')
    for i in path:
        tmpIm = cStringIO.StringIO(i.read())
        print tmpIm
        img = Image.open(tmpIm)
        size = {'height': img.size[0], 'width': img.size[1]}
        print size
        # <cStringIO.StringI object at 0x7f6dcdf57828>

    return jsonify({'username': user.name})


@_main.route('/api/token', methods=['POST'])
@auth.login_required
def get_auth_token():
    from sqlalchemy import func
    collection_id = 22
    # collection = Collection.query.filter_by(id=collection_id).first()
    a = Image.query(func.count('*')).filter_by(collection_id=collection_id, status=0).all()
    # a = db.session.query(func.count('*')).filter_by(collection_id=collection_id).all()
    # a = db.session.query(func.count('*')).filter(Image.collection_id==collection_id, Image.version_id.is_(None)).scalar()
    print a
    return 'ok'
    #
    # a = request.form.to_dict()
    # token = g.user.generate_auth_token(600)
    # return jsonify({'token': token.decode('ascii'), 'duration': 600})


@_main.route('/data_module/create_dataset', methods=['POST'])
@auth.login_required
def create_data():
    """
    创建数据集
    :return:
    """
    local_time = time.time()

    # token = g.user.generate_auth_token(600)
    # print token

    name = request.form['name']  # 集合标题
    desc = request.form['desc']  # 集合描述
    data_type = request.form['data_type']  # 集合类型(分类/检测/分割)(int)
    if not all([name, desc, data_type]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')

    label_type = request.form.get('label_type')  # 标注类别(猫/狗)  ########## 单独定义
    upload_file = request.files.get('upload_file')  # 上传标签地址
    try:
        user = db.session.query(Collection.name).filter(Collection.user_id == g.user.id).all()
        data_list = [x.name for x in user]  # 所有数据集名字
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(err_no=RET.DBERR, err_desc='查询出错')
    if name in data_list:
        return jsonify(err_no=RET.DBERR, err_desc='集合名称已经存在')

    collection = Collection()
    collection.user_id = g.user.id
    collection.name = name
    collection.desc = desc
    collection.type = data_type
    if upload_file is None and label_type is None:
        return jsonify(errno=RET.PARAMERR, errmsg='标签不能为空')
    try:
        db.session.add(collection)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(err_no=RET.DBERR, err_desc='保存失败')
    try:
        dataset_id = db.session.query(Collection.id).filter_by(user_id=g.user.id, name=name).scalar()  # 集合id
        if upload_file:
            data = upload_file.read()
            for i in data.split('\n'):
                if i is '':
                    break
                label = Label()
                label.label_id = i.split(':')[0]
                label.name = i.split(':')[1]
                label.collection_id = dataset_id
                try:
                    db.session.add(label)
                    db.session.commit()
                except Exception as e:
                    current_app.logger.error(e)
                    db.session.rollback()
                    return jsonify(err_no=RET.DBERR, err_desc='上传标签保存失败')

        if label_type:
            for i in label_type.split(','):
                label = Label()
                label.label_id = i.split(':')[0]
                label.name = i.split(':')[1]
                label.collection_id = dataset_id
                try:
                    db.session.add(label)
                    db.session.commit()
                except Exception as e:
                    current_app.logger.error(e)
                    db.session.rollback()
                    return jsonify(err_no=RET.DBERR, err_desc='当前标签保存失败')

    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(err_no=RET.DBERR, err_desc='保存标签失败')

    request_id = (request.cookies.get('session'))[:36]
    time_used = int((time.time() * 1000) - int(local_time * 1000))
    return jsonify(err_no=RET.OK, err_desc='OK',
                   dataset_id=dataset_id, request_id=request_id,
                   time_used=time_used)


@_main.route('/data_module/delete_dataset', methods=['DELETE'])
@auth.login_required
def delete_data():
    """
    删除数据集
    :return:
    """
    local_time = time.time()
    user_data = request.get_json()
    if not user_data:
        return jsonify(err_no=RET.PARAMERR, err_desc='参数缺失')
    name = user_data.get('name')
    if not name:
        return jsonify(err_no=RET.PARAMERR, err_desc='参数缺失')
    try:
        collection = Collection.query.filter_by(user_id=g.user.id, name=name).first()
        if collection.images:
            for i in collection.images:
                if i.site:
                    fun.remove(i.site.encode())
                if i.label_path:
                    fun.remove(i.label_path.encode())
                db.session.delete(i)
                db.session.commit()
        if collection.labels:
            for i in collection.labels:
                db.session.delete(i)
                db.session.commit()
        db.session.delete(collection)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(err_no=RET.DBERR, err_desc='信息保存异常')
    request_id = (request.cookies.get('session'))[:36]
    time_used = int((time.time() * 1000) - int(local_time * 1000))

    return jsonify(err_no=RET.OK, err_desc='OK',
                   request_id=request_id, time_used=time_used
                   )


# @_main.route('/data_module/update_dataset', methods=['PUT'])
# @auth.login_required
# def update_data():
#     """
#     更改数据集
#     :return:
#     """
#     local_time = time.time()
#     user_data = request.get_json()
#     if not user_data:
#         return jsonify(err_no=RET.PARAMERR, err_desc='参数缺失')
#     name = user_data.get('name')
#     if not name:
#         return jsonify(err_no=RET.PARAMERR, err_desc='参数缺失')
#     try:
#         Collection.query.filter_by(id=g.user.id).update({'name': name})
#         db.session.commit()
#     except Exception as e:
#         current_app.logger.error(e)
#         db.session.rollback()
#         return jsonify(err_no=RET.DBERR, err_desc='信息保存异常')
#     # session['name'] = name
#     request_id = (request.cookies.get('session'))[:36]
#     time_used = int((time.time() * 1000) - int(local_time * 1000))
#     return jsonify(err_no=RET.OK, err_desc='OK',
#                    request_id=request_id, time_used=time_used
#                    )


@_main.route('/data_module/list_dataset', methods=['GET'])
@auth.login_required
def get_index():
    """
    数据集--列表
    :return:
    """
    local_time = time.time()
    try:
        user = User.query.filter_by(id=g.user.id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, err_desc='查询数据库错误')
    try:
        collection = redis_store.get('my_collection')
    except Exception as e:
        current_app.logger.error(e)
        collection = None
    if collection:
        current_app.logger.info('%s' % g.user.id)
        return '{"err_no":0,"err_desc":"OK","data":%s}' % collection

    try:
        collection = user.collections
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(err_no=RET.DBERR, err_desc='查询数据集信息异常')
    if not collection:
        return jsonify(errno=RET.NODATA, err_desc='无数据集信息')
    my_list = []
    for i in collection:
        my_list.append(i.to_dict())
    my_json = json.dumps(my_list)
    try:
        redis_store.setex('my_collection', 7200, my_json)
    except Exception as e:
        current_app.logger.error(e)

    request_id = (request.cookies.get('session'))[:36]
    time_used = int((time.time() * 1000) - int(local_time * 1000))

    resp = '{"err_no": 0, "err_desc": "OK", "time_used": %s, "request_id":%s, "data": %s}' % \
           (time_used, request_id, my_json)
    return resp


@_main.route('/data_module/<int:collection_id>', methods=['GET'])
@auth.login_required
def collection_info(collection_id):
    """
    数据集--详情
    :return:
    """
    local_time = time.time()
    try:
        ret = redis_store.get('data_info_%s' % collection_id)
    except Exception as e:
        current_app.logger.error(e)
        ret = None
    if ret:
        current_app.logger.info('hit redis personage detail info')
        return '{"err_no:0","err_desc:OK","data":%s}' % ret
    try:
        collection = Collection.query.filter_by(id=collection_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(err_no=RET.DBERR, err_desc='Query collection failed')
    if not collection:
        return jsonify(err_no=RET.DBERR, err_desc='No such dataset')
    try:
        collection_data = collection.to_dict()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(err_no=RET.DBERR, err_desc='The query fails')
    collection_json = json.dumps(collection_data)
    try:
        redis_store.setex('data_info_%s' % collection_id, 7200, collection_json)
    except Exception as e:
        current_app.logger.error(e)

    request_id = (request.cookies.get('session'))[:36]
    time_used = int((time.time() * 1000) - int(local_time * 1000))
    data = {"user_id": g.user.id, "collection": collection_json}
    resp = '{"err_no:0", "err_desc:OK", "time_used": %s, "request_id":%s, "data": %s}' % (request_id, time_used, data)
    return resp
