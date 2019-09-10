# -*- coding:utf-8 -*-
import time

from flask import json
from sqlalchemy import func

from DataSet.models import Version
from DataSet.token.auths import auth
from flask import current_app, request, jsonify, g
from DataSet import db, redis_store
from DataSet.models import Collection, Image, Label
from DataSet.utils.change_json_file import storage, cjf
from DataSet.utils.create_label_file import clf, image_size
from DataSet.utils.serial_code import RET
from DataSet.api_0_1.main import _main


@_main.route('/data_module/upload_image/<collection_name>', methods=['POST'])
@auth.login_required
def upload_image(collection_name):
    """
    上传图片 分类/人脸
    """
    local_time = time.time()
    try:
        collection = Collection.query.filter_by(user_id=g.user.id,
                                                name=collection_name).first()  # 当前集合
        if collection is None:
            return jsonify(err_no=RET.PARAMERR, err_desc='没有该数据集')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(err_no=RET.PARAMERR, err_desc='参数有误')

    status = request.form['status']

    if not status:
        return jsonify(err_on=RET.PARAMERR, err_desc='参数不完整')
    upload_image_site = request.files.getlist('upload_image_site')  # 图片文件
    table_site = request.files.get('table_site')  # 对应表文件
    label_id = [l_id.label_id for l_id in collection.labels]
    label_name = [l_name.name.encode('utf-8') for l_name in collection.labels]
    if status == 'add_label':
        # 新增
        new_label = request.form['new_label']
        if new_label is None:
            return jsonify(err_no=RET.NODATA, err_desc='名称参数缺失')

        if new_label.split(':')[0] in label_id or new_label.split(':')[1] in label_name:
            return jsonify(err_no=RET.NODATA, err_desc='该标签或id以存在')

        try:
            label = Label()
            label.name = new_label.split(':')[1]
            label.label_id = new_label.split(':')[0]
            label.collection_id = collection.id
            db.session.add(label)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
        return jsonify(err_no='ok')

    if not upload_image_site:
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')

    if status == 'appoint_table':
        # 对应表
        if table_site is None:
            return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
        try:
            table_name = table_site.read()
            table_list = []
            for i in table_name.split('\r\n'):
                table_list.append(i.split(':')[0])
            for up_file in upload_image_site:
                tables = table_name.split(up_file.filename + ':')[1]
                images = storage(up_file, collection)
                size = image_size(up_file)
                labels = Label.query.filter_by(name=tables.split('\r\n')[0]).first()
                if up_file.filename in table_list and \
                        labels is not None:

                    # 标注上传
                    clf.classification(images, size, labels.label_id,
                                       labels.name)

                else:
                    clf.default(images, size)
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(err_no=RET.DBERR, err_desc='图片保存失败')
        return jsonify(err_no=RET.OK, err_desc='OK')

    if status == 'default':
        # 未标注
        if not upload_image_site:
            return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
        try:
            for up_file in upload_image_site:
                images = storage(up_file, collection)
                size = image_size(up_file)
                clf.default(images, size)
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(err_no=RET.DBERR, err_desc='图片保存失败')
        return jsonify(err_no=RET.OK, err_desc='OK')

    if status.split(':')[1] in label_name:
        # 标注上传
        try:
            label_data = Label.query.filter_by(name=status.split(':')[1]).first()
            if label_data is None:
                return jsonify(err_no=RET.PARAMERR, err_desc='没有此标签')
            if not upload_image_site:
                return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')

            if int(status.split(':')[0]) != label_data.label_id:
                return jsonify(errno=RET.PARAMERR, errmsg='错误的标签ID')
            for up_file in upload_image_site:
                images = storage(up_file, collection)
                size = image_size(up_file)
                clf.classification(images, size, status.split(':')[0],
                                   status.split(':')[1])
        except Exception as e:
            # fun.remove(image_status.get('file_id'))
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(err_no=RET.DBERR, err_desc='图片保存失败')
    else:
        return jsonify(err_no=RET.DBERR, err_desc='无效参数')
    request_id = (request.cookies.get('session'))[:36]
    time_used = int((time.time() * 1000) - int(local_time * 1000))
    return jsonify(err_no=RET.OK, err_desc='OK',
                   dataset_id=collection.id, request_id=request_id,
                   time_used=time_used)


@_main.route('/data_module/upload_images/<collection_name>', methods=['POST'])
@auth.login_required
def upload_images(collection_name):
    """
    上传图片 检测/分割
    """
    local_time = time.time()
    try:
        collection = Collection.query.filter_by(user_id=g.user.id,
                                                name=collection_name).first()  # 当前集合
        if collection is None:
            return jsonify(err_no=RET.PARAMERR, err_desc='没有该数据集')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(err_no=RET.PARAMERR, err_desc='参数有误')

    status = request.form.get('status')

    upload_image_site = request.files.getlist('upload_image_site')  # 图片文件
    label_file = request.files.getlist('label_file')  # 标注文件
    table_site = request.files.get('table_site')  # 对应表文件

    if status == 'default':
        # 未标注
        try:
            if not upload_image_site:
                return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
            for up_file in upload_image_site:
                images = storage(up_file, collection)
                size = image_size(up_file)
                clf.default(images, size)

        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(err_no=RET.DBERR, err_desc='图片保存失败')
        return jsonify(err_no=RET.OK, err_desc='OK')

    if not upload_image_site and not label_file:
        return jsonify(err_no=RET.PARAMERR, err_desc='缺少图片文件或标记文件')

    label_file_name = []  # 标注列表名，有后缀
    label_list = []  # 标注列表名，无后缀
    for l_file in label_file:
        label_file_name.append(l_file.filename)
        label_list.append(l_file.filename.split('.')[0])

    if status is None:
        # 已经标注上传，未选择对应表
        for up_file in upload_image_site:
            try:
                images = storage(up_file, collection)
                size = image_size(up_file)
                if up_file.filename.split('.')[0] in label_list:
                    for l_file in label_file:
                        if up_file.filename.split('.')[0] + '.' + l_file.filename.split('.')[1] == l_file.filename:
                            if l_file.filename.split('.')[1] == 'xml':
                                clf.segmentation(images, size, l_file, collection)
                            elif l_file.filename.split('.')[1] == 'json':
                                cjf.segmentation(images, size, l_file)
                            else:
                                clf.default(images, size)
                        else:
                            continue
                else:
                    # 未标注
                    clf.default(images, size)

            except Exception as e:
                current_app.logger.error(e)
                db.session.rollback()
                return jsonify(err_no=RET.DBERR, err_desc='图片保存失败')
        return jsonify(err_no=RET.OK, err_desc='OK')

    if not status:
        return jsonify(err_on=RET.PARAMERR, err_desc='参数不完整')

    if status == 'appoint_table':
        # 对应表
        if not table_site:
            return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
        try:
            table_str = table_site.read()
            table_name_list = []  # 对应表,图片名
            table_file_list = []  # 对应表，标注文件名

            for i in table_str.split('\r\n'):
                table_name_list.append(i.split(':')[0])

                table_file_list.append(i.split(':')[1])
            for up_file in upload_image_site:
                images = storage(up_file, collection)
                size = image_size(up_file)
                if up_file.filename in table_name_list and \
                        table_str.split(up_file.filename + ':')[1].split('\r\n')[0] in label_file_name:
                    for l_file in label_file:
                        if up_file.filename.split('.')[0] + '.' + l_file.filename.split('.')[1] == l_file.filename:
                            if l_file.filename.split('.')[1] == 'xml':
                                clf.segmentation(images, size, l_file, collection)
                            elif l_file.filename.split('.')[1] == 'json':
                                cjf.segmentation(images, size, l_file)
                            else:
                                clf.default(images, size)
                        else:
                            continue
                else:
                    clf.default(images, size)
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(err_no=RET.DBERR, err_desc='图片保存失败')

    request_id = (request.cookies.get('session'))[:36]
    time_used = int((time.time() * 1000) - int(local_time * 1000))
    return jsonify(err_no=RET.OK, err_desc='OK',
                   dataset_id=collection.id, request_id=request_id,
                   time_used=time_used)


@_main.route('/data_module/<int:collection_id>/versions_info', methods=['POST'])
@auth.login_required
def versions_info(collection_id):
    """版本列表页/详情"""
    local_time = time.time()
    try:
        collection = Collection.query_filter_by(id=collection_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(err_no=RET.DBERR, err_desc='参数有误')
    if collection is None:
        return jsonify(err_no=RET.PARAMERR, err_desc='没有该数据集')

    try:
        versions = redis_store.get('versions_info')
    except Exception as e:
        current_app.logger.error(e)
        versions = None
    if versions:
        current_app.logger.info('%s' % g.user.id)
        return '{"err_no":0,"err_desc":"OK","data":%s}' % versions

    versions = [version.to_dict for version in collection.versions]
    my_json = json.dumps(versions)
    try:
        redis_store.setex('versions_info', 7200, my_json)
    except Exception as e:
        current_app.logger.error(e)

    request_id = (request.cookies.get('session'))[:36]
    time_used = int((time.time() * 1000) - int(local_time * 1000))
    resp = '{"err_no": 0, "err_desc": "OK", "time_used": %s, "request_id":%s, "data": %s}' % \
           (time_used, request_id, my_json)
    return resp


@_main.route('/data_module/<int:collection_id>/create_versions', methods=['POST'])
@auth.login_required
def create_versions(collection_id):
    """版本创建"""
    local_time = time.time()
    try:
        collection = Collection.query_filter_by(id=collection_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(err_no=RET.DBERR, err_desc='参数有误')
    if collection is None:
        return jsonify(err_no=RET.PARAMERR, err_desc='没有该数据集')

    name = request.get_json('name')
    desc = request.get_json('desc')
    image_count = request.get_json('image_count')
    old_version = request.get_json('old_version')
    if not name:
        return jsonify(err_no=RET.PARAMERR, err_desc='参数错误')

    data_list = [x.name for x in collection.versions]

    if name in data_list:
        return jsonify(err_no=RET.DATAERR, err_desc='版本名称以存在')

    number = db.session.query(func.count('*')).filter(
        Image.collection_id == collection_id, Image.version_id.is_(None)).scalar()  # 无版本图片总和

    if image_count > number:
        return jsonify(err_no=RET.PARAMERR, err_desc='参数错误', data='当前可选图片值最大为{}'.format(number))

    versions_list_name = [c_version.name for c_version in collection.versions]
    if old_version not in versions_list_name:
        return jsonify(err_no=RET.PARAMERR, err_desc='找不到该版本')
    try:
        versions = Version.query_filter_by(collection_id=collection_id, name=old_version).first()  # 原版本
        images = Image.query_filter_by(version_id=versions.id).all()  # 查出原版本下所有图片

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(err_no=RET.DBERR, err_desc='参数有误')

    if image_count:
        version = Version()
        version.name = name
        version.description = desc
        version.collection_id = collection_id
        db.session.add(version)
        db.session.commit()
        no_version = db.session.query(func.count('*')).filter(
            Image.collection_id == collection_id, Image.version_id.is_(None)).limit(50)  # 前50张图片
        for n_version in no_version:
            version.images = n_version.image
            db.session.add(version)
            db.session.commit()

        request_id = (request.cookies.get('session'))[:36]
        time_used = int((time.time() * 1000) - int(local_time * 1000))
        return jsonify(err_no=RET.OK, err_desc='OK',
                       dataset_id=collection.id, request_id=request_id,
                       time_used=time_used)

    # try:
    #     new_version = Version.query.filter_by(collection_id=collection_id, name=name).first()
    #     for i in images:
    #         i.version_id = new_version.id
    #         db.session.add(version)
    #         db.session.commit()
    #     db.session.delete(versions)
    #     db.session.commit()
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(err_no=RET.DBERR, err_desc='参数有误')

    request_id = (request.cookies.get('session'))[:36]
    time_used = int((time.time() * 1000) - int(local_time * 1000))
    return jsonify(err_no=RET.OK, err_desc='OK',
                   dataset_id=collection.id, request_id=request_id,
                   time_used=time_used)

# @api.route('/data_module/remove_images', methods=['DELETE'])
# @login_request

#     """
#     删除文件
#     """

# @api.route('/data_module/download_images', methods=['GET'])
# @login_request

#     """
#     下载文件
#     """
