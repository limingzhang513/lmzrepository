# -*- coding:utf-8 -*-
import cStringIO
import os
import time
import urllib2
import zipfile
from io import BytesIO
from sqlalchemy import func
from DataSet import db, redis_store
from DataSet.fastdfs.view import fun
from DataSet.token.auths import auth
from DataSet.api_0_1.main import _main
from DataSet.utils import commons
from DataSet.utils.serial_code import RET
from DataSet.models import User, Version, Collection, Image
from flask import current_app, request, jsonify, g, send_file, json, make_response
from DataSet.utils.auth_decorator import user_required, user_identification


@_main.route('/data_module/<int:collection_id>/versions_info', methods=['GET'])
def versions_info(collection_id):
    """版本列表页/详情"""
    local_time = time.time()
    result = auth.identify(request)
    if 0 == result['err_no'] and result['data']:
        collection = user_identification(collection_id, result['data'])
        if not collection:
            return jsonify(commons.falseReturn(RET.DBERR, '', '不存在的数据集'))

        # try:
        #     versions = redis_store.get('versions_info_%s' % collection_id)
        # except Exception as e:
        #     current_app.logger.error(e)
        #     versions = None
        # if versions:
        #     current_app.logger.info('%s' % g.user.id)
        #     request_id = (request.cookies.get('session'))[:36]
        #     time_used = int((time.time() * 1000) - int(local_time * 1000))
        #     return '{"err_no": "0", "err_desc": "OK", "time_used": %s, "request_id":"%s", "data": %s}' % \
        #            (time_used, request_id, versions)

        versions = []
        for version in collection.versions:
            number = db.session.query(func.count('*')).filter(Image.version_id == version.id).scalar()
            versions_dict = version.to_dict()
            versions_dict['image_count'] = number
            versions_dict['labels'] = eval(str(version.label_info))
            versions.append(versions_dict)
        
        # other images
        vs_0 = dict()
        number_labeled = db.session.query(func.count('*')).filter(
            Image.collection_id == collection_id, Image.status == 3, Image.version_id.is_(None)).scalar()  # 查以标注 没有分配版本的总和
        vs_0[ 'version_name' ] = '未生成版本'
        vs_0[ 'version_description' ] = '包含所有已标注但未生成版本的图片'
        vs_0[ 'version_id' ] = -1
        vs_0[ 'image_count' ] = int( number_labeled )
        vs_0[ "labels" ] = dict()
        versions.append( vs_0 )
        
        my_json = json.dumps(versions)

        # try:
        #     redis_store.setex('versions_info_%s' % collection_id, 7200, my_json)
        # except Exception as e:
        #     current_app.logger.error(e)

        try:
            request_id = request.cookies.get('session')[:36]
        except TypeError:
            request_id = {}
        time_used = int((time.time() * 1000) - int(local_time * 1000))

        resp = {"time_used": time_used, "request_id": request_id, "versions": json.loads(my_json)}
        return jsonify(commons.trueReturn(resp, "OK"))
    else:
        return jsonify(result)


@_main.route('/data_module/<int:collection_id>/versions_all', methods=['GET'])
@user_required
def version_all(collection_id):
    """--版本获取--"""
    local_time = time.time()
    collection = user_identification(collection_id, g.user.id)
    if not collection:
        return jsonify(err_no=RET.DBERR, err_desc='不存在的数据集')

    # try:
    #     version = redis_store.get('version_info_%s' % collection_id)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     version = None
    # if version:
    #     current_app.logger.info('%s' % g.user.id)
    #     request_id = (request.cookies.get('session'))[:36]
    #     time_used = int((time.time() * 1000) - int(local_time * 1000))
    #     return '{"err_no": "0", "err_desc": "OK", "time_used": %s, "request_id":"%s", "data": %s}' % \
    #            (time_used, request_id, version)

    datas = []
    for i in collection.versions:
        datas.append(i.name)
    json_data = json.dumps(datas)

    # try:
    #     redis_store.setex('version_info_%s' % collection_id, 7200, json_data)
    # except Exception as e:
    #     current_app.logger.error(e)
    try:
        request_id = request.cookies.get('session')[:36]
    except TypeError:
        request_id = {}
    time_used = int((time.time() * 1000) - int(local_time * 1000))
    data = {'dataset_id': collection.id, 'request_id': request_id, 'time_used': time_used, 'versions_name': datas}
    return jsonify(commons.trueReturn(data, 'OK'))


@_main.route('/data_module/<int:collection_id>/create_versions', methods=['POST'])
@user_required
def create_versions(collection_id):
    """版本创建"""
    local_time = time.time()
    collection = user_identification(collection_id, g.user.id)
    if not collection:
        return jsonify(commons.falseReturn(RET.DBERR, '', '不存在的数据集'))

    version_data = request.get_json()
    if not version_data:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '参数错误'))
    name = version_data.get('name')
    desc = version_data.get('desc')
    image_count = version_data.get('image_count')
    old_version = version_data.get('old_version')
    if not name or (not int(image_count) and not old_version) or not desc:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '参数缺失'))
    data_list = [x.name for x in collection.versions]

    if name in data_list:
        return jsonify(commons.falseReturn(RET.DATAERR, '', '版本名称以存在'))

    number = db.session.query(func.count('*')).filter(
        Image.collection_id == collection_id, Image.status == 3, Image.version_id.is_(None)).scalar()  # 查以标注 没有分配版本的总和

    if int(image_count) > number:
        return jsonify(commons.falseReturn(RET.PARAMERR, '当前可选图片值最大为{}'.format(number), '参数错误'))
    version = Version()
    version.name = name
    version.description = desc
    version.collection_id = collection_id
    db.session.add(version)
    db.session.commit()
    from DataSet.celery_tasks.tasks import create_version
    create_version.delay(collection_id, name, image_count, old_version)

    try:
        request_id = request.cookies.get('session')[:36]
    except TypeError:
        request_id = {}
    time_used = int((time.time() * 1000) - int(local_time * 1000))
    data = {'dataset_id': collection.id, 'request_id': request_id, 'time_used': time_used}
    return jsonify(commons.trueReturn(data, 'OK'))


@_main.route('/data_module/<int:version_id>/delete_versions', methods=['DELETE'])
@user_required
def delete_versions(version_id):
    """版本删除"""
    local_time = time.time()
    try:
        versions = db.session.query(Version).filter(
            Collection.user_id == g.user.id, Version.id == version_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(commons.falseReturn(RET.DBERR, '', '参数有误'))
    if versions is None:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '没有该版本'))
    data_json = request.get_json('status')
    if not data_json:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '参数缺失'))
    status = data_json['status']

    from DataSet.celery_tasks.tasks import delete_version
    delete_version.delay(status, version_id)

    try:
        request_id = request.cookies.get('session')[:36]
    except TypeError:
        request_id = {}
    time_used = int((time.time() * 1000) - int(local_time * 1000))
    data = {'dataset_id': versions.collection_id, 'request_id': request_id, 'time_used': time_used}
    return jsonify(commons.trueReturn(data, 'OK'))


@_main.route('/data_module/download_images', methods=['GET'])
def download_images():
    """版本下载"""

    collection_id = request.values.get('collection_id', None)  # int
    version_id = request.values.get('version_id', None)  # int
    if not all([collection_id, version_id]):
        return jsonify(err_no=RET.PARAMERR, err_desc='参数缺失')
    collection = user_identification(collection_id, 1)
    if not collection:
        return jsonify(err_no=RET.DBERR, err_desc='不存在的数据集')
    versions = [x.id for x in collection.versions]
    # # no_list = list(set(version_id).intersection(set(versions)))  # 交集
    # for i in version_id:
    if version_id not in versions:
        return jsonify(err_no=RET.DBERR, err_desc='不存在的版本')

    version = Version.query.filter_by(id=version_id).first()
    label_url_path = current_app.config['NGINX_SITE'] + fun.getInfo(version.zip_path)['group_file_id']
    files = urllib2.urlopen(label_url_path)
    tmpIm = cStringIO.StringIO(files.read())
    return send_file(tmpIm, attachment_filename=version.name + '.zip', as_attachment=True, add_etags=False)


@_main.route('/data_module/<int:collection_id>/share', methods=['PATCH'])
@user_required
def collection_share(collection_id):
    """数据集分享"""
    local_time = time.time()
    data_json = request.get_json()
    user_id = data_json.get('user_id')
    if not user_id:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '分享id不能为空'))
    try:
        collection = Collection.query.filter_by(user_id=g.user.id, id=collection_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(commons.falseReturn(RET.DBERR, '', '参数有误'))
    if collection is None:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '没有该数据集'))

    user = User.query.filter_by(id=user_id).first()  # 被分享的用户id
    share_user = user.share
    if not share_user.share_collection:
        share_user.share_collection = str([collection_id])
    else:
        data_id = eval(share_user.share_collection)
        data_id.append(collection_id)
        share_user.share_collection = str(data_id)  # 分享的数据集

    users = User.query.filter_by(id=g.user.id).first()
    share_users = users.share
    my_share = share_users.my_share  # 我的分享 str
    if not my_share:
        dict_my_share = {user_id: [collection_id]}
    else:
        dict_my_share = eval(my_share)  # 将字符串转成字典
        list_my_share_value = dict_my_share.get(str(user_id))  # 查出都分享给了这个用户那些数据集 list[1,2,3]
        if not list_my_share_value:
            dict_my_share[str(user_id)] = [collection_id]  # 没有就添加这个用户
        else:
            if collection_id not in dict_my_share[str(user_id)]:
                dict_my_share[str(user_id)].append(collection_id)  # 没有就添加这个数据集
            else:
                return jsonify(commons.falseReturn(RET.DATAERR, '', '请不要重复添加'))

    share_users.my_share = json.dumps(dict_my_share)  # 还原字符串
    db.session.add_all([share_user, share_users])
    db.session.commit()
    data = {'my_share': eval(share_users.my_share), 'share_collection': eval(share_user.share_collection)}
    try:
        request_id = request.cookies.get('session')[:36]
    except TypeError:
        request_id = {}
    time_used = int((time.time() * 1000) - int(local_time * 1000))
    data = {'dataset_id': collection.id, 'request_id': request_id, 'time_used': time_used, 'data': data}
    return jsonify(commons.trueReturn(data, 'OK'))


@_main.route('/data_module/<int:collection_id>/cancel_share', methods=['PATCH'])
@user_required
def collection_cancel_share(collection_id):
    """数据集取消分享"""
    local_time = time.time()
    data_json = request.get_json()
    user_id = data_json.get('user_id')
    if not user_id:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '用户id不能为空'))
    try:
        collection = Collection.query.filter_by(user_id=g.user.id, id=collection_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(commons.falseReturn(RET.DBERR, '', '参数有误'))
    if collection is None:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '没有该数据集'))

    user = User.query.filter_by(id=user_id).first()  # 被分享的用户id
    share_user = user.share
    if not share_user.share_collection:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '该数据集没有分享给此用户'))
    if collection_id not in eval(share_user.share_collection):
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '该数据集没有分享给此用户2'))

    # 删除对方
    data_id = eval(share_user.share_collection)
    data_id.remove(collection_id)
    if not data_id:
        share_user.share_collection = None
    else:
        share_user.share_collection = str(data_id)  # 分享的数据集

    users = User.query.filter_by(id=g.user.id).first()
    share_users = users.share
    my_share = share_users.my_share  # 我的分享 str
    if not my_share:
        return jsonify(commons.falseReturn(RET.DATAERR, '', '您未向他人分享过数据集'))

    dict_my_share = eval(my_share)  # 将字符串转成字典
    list_my_share_value = dict_my_share.get(str(user_id))  # 查出都分享给了这个用户那些数据集 list[1,2,3]
    if not list_my_share_value:
        return jsonify(commons.falseReturn(RET.DATAERR, '', '您未向该用户分享过数据集'))
    if collection_id in dict_my_share[str(user_id)]:
        dict_my_share[str(user_id)].remove(collection_id)  # 有就删除这个数据集

    if not dict_my_share[str(user_id)]:
        del dict_my_share[str(user_id)]
    if not dict_my_share:
        share_users.my_share = None

    share_users.my_share = (json.dumps(dict_my_share) if dict_my_share else None)  # 还原字符串
    db.session.add_all([share_user, share_users])
    db.session.commit()
    data = {'my_share': eval(share_users.my_share) if share_users.my_share else None,
            'share_collection': eval(share_user.share_collection) if share_user.share_collection else None}
    try:
        request_id = request.cookies.get('session')[:36]
    except TypeError:
        request_id = {}
    time_used = int((time.time() * 1000) - int(local_time * 1000))
    data = {'dataset_id': collection.id, 'request_id': request_id, 'time_used': time_used, 'data': data}

    return jsonify(commons.trueReturn(data, 'OK'))

