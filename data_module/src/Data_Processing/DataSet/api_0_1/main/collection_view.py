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


@_main.route('/api/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)  # 获取用户name
    return jsonify({'username': user.name})


@_main.route('/api/token', methods=['GET'])
def get_auth_token():
    # a = request.form.to_dict()
    """大概思路局势"""
    print request.path
    print request.url
    print request.url_root
    print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return jsonify({'token': '废弃接口'})


@_main.route('/data_module/create_dataset', methods=['POST'])
@user_required
def create_data():
    """
    创建数据集
    :return:
    """
    local_time = time.time()
    name = request.form.get('name')  # 集合标题
    desc = request.form.get('desc')  # 集合描述
    data_type = request.form.get('data_type')  # 集合类型(分类/检测/分割)(int)
    if not all([name, desc, data_type]):
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '参数缺失'))
    label_type = request.form.get('label_type').split(",")  # 标注类别(猫/狗)  ########## 单独定义
    print label_type
    upload_file = request.files.get('upload_file')  # 上传标签地址
    try:
        # g已在用户权鉴Auths模块中设定（装饰器中）
        user = db.session.query(Collection.name).filter(Collection.user_id == g.user.id).all()
        data_list = [x.name for x in user]  # 所有数据集名字
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(commons.falseReturn(RET.DBERR, '', '查询出错'))
    if name in data_list:
        return jsonify(commons.falseReturn(RET.DBERR, '', '集合名称已经存在'))
    collection = Collection()
    collection.user_id = g.user.id
    collection.name = name
    collection.desc = desc
    collection.type = data_type
    if not upload_file and not label_type:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '标签不能为空'))
    try:
        db.session.add(collection)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(commons.falseReturn(RET.DBERR, '', '保存失败'))
    try:
        # scalar()返回查询结果第一个元素
        dataset_id = db.session.query(Collection.id).filter_by(user_id=g.user.id, name=name).scalar()  # 集合id
        if upload_file:
            data = upload_file.read()
            for i in data.split('\n'):
                if (i.split(':')[0] or i.split(':')[1]) is None:
                    continue
                    # Label.query.filter_by(collection_id=g.user.id, name=i.split(':')[1]).delete()
                    # db.session.commit()
                    # break
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
                    return jsonify(commons.falseReturn(RET.DBERR, '', '上传标签保存失败'))
        elif label_type:
            for i in label_type:
                print label_type
                print i
                if label_type.count(i) > 1:
                    continue
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
                    return jsonify(commons.falseReturn(RET.DBERR, '', '当前标签保存失败'))
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(commons.falseReturn(RET.DBERR, '', '保存标签失败'))
    try:
        request_id = request.cookies.get('session')[:36]
    except TypeError:
        request_id = {}
    time_used = int((time.time() * 1000) - int(local_time * 1000))  # 使用时间毫秒
    data = {'dataset_id': dataset_id, 'request_id': request_id, 'time_used': time_used}
    return jsonify(commons.trueReturn(data, 'OK'))


@_main.route('/data_module/label_type/<collection_id>', methods=['GET'])
@user_required
def label_type(collection_id):
    """--标签类别--"""
    local_time = time.time()

    collection = user_identification(collection_id, g.user.id)
    if not collection:
        return jsonify(commons.falseReturn(RET.DBERR, '', '不存在的数据集'))
    # try:
    #     labels = redis_store.get('labels_info_%s' % collection_id)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     labels = None
    # if labels:
    #     current_app.logger.info('%s' % g.user.id)
    #     request_id = (request.cookies.get('session'))[:36]
    #     time_used = int((time.time() * 1000) - int(local_time * 1000))
    #     data = {"time_used": time_used, "request_id": request_id, "data": labels}
    #     return jsonify(commons.trueReturn(data, 'OK'))

    label_list = []
    for i in collection.labels:
        label_list.append(i.to_dict())
    # json_data = json.dumps(label_list)

    # try:
    #     redis_store.setex('labels_info_%s' % collection_id, 7200, json_data)
    # except Exception as e:
    #     current_app.logger.error(e)

    try:
        request_id = request.cookies.get('session')[:36]
    except TypeError:
        request_id = {}
    time_used = int((time.time() * 1000) - int(local_time * 1000))
    data = {'dataset_id': collection.id, 'request_id': request_id, 'time_used': time_used, 'labels': label_list}
    return jsonify(commons.trueReturn(data, 'OK'))


@_main.route('/data_module/upload_image/<collection_id>', methods=['POST'])
@user_required
def upload_image(collection_id):
    """
    上传图片 分类/人脸
    """
    local_time = time.time()
    collection = user_identification(collection_id, g.user.id)  # 当前集合
    if not collection:
        return jsonify(commons.falseReturn(RET.DBERR, '', '不存在的数据集'))
    if 1 != collection.type:
        return jsonify(commons.falseReturn(RET.DATAERR, '', '请选择正确的数据集类型进行上传'))
    status = request.form['status']  # 标注状态
    if not status:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '参数不完整'))

    label_id = [l_id.label_id for l_id in collection.labels]
    label_name = [l_name.name.encode('utf-8') for l_name in collection.labels]
    if status == 'add_label':
        print status
        # 新增celery -A DataSet.celery_tasks.tasks:celery worker --loglevel=info
        # gunicorn -b 192.168.1.137:5000 manage:app
        #  -w 4 -b 0.0.0.0:8080 main:app
        # gunicorn
        new_label = request.form['new_label']
        if new_label is None:
            return jsonify(commons.falseReturn(RET.NODATA, '', '名称参数缺失'))

        if new_label.split(':')[0] in label_id or new_label.split(':')[1] in label_name:
            return jsonify(commons.falseReturn(RET.NODATA, '', '该标签或id以存在'))

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
        try:
            request_id = request.cookies.get('session')[:36]
        except TypeError:
            request_id = {}
        time_used = int((time.time() * 1000) - int(local_time * 1000))
        print 111111
        data = {'dataset_id': collection.id, 'request_id': request_id, 'time_used': time_used}
        return jsonify(commons.trueReturn(data, 'OK'))
    print 22222
    upload_image_site = request.files.getlist('upload_image_site')  # 图片文件列表
    table_site = request.files.get('table_site')  # 对应表文件
    if table_site:
        table_site = table_site.read()
    if not upload_image_site:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '参数缺失'))
    # if len(upload_image_site) > 100:
    # return jsonify(commons.falseReturn(RET.PARAMERR, '当前已选图片{}张'.format(len(upload_image_site)), '超过图片最大限制100'))

    image_dict = {}
    for i in upload_image_site:
        image_dict[i.filename] = base64.b64encode(i.read())  # 以图片名为键，读取的图片二进制码为值保存在image_dict中
    from DataSet.celery_tasks.tasks import classification
    classification.delay(status, table_site, image_dict, collection_id, label_name)
    try:
        request_id = request.cookies.get('session')[:36]
    except TypeError:
        request_id = {}
    time_used = int((time.time() * 1000) - int(local_time * 1000))

    data = {'dataset_id': collection.id, 'request_id': request_id, 'time_used': time_used}
    return jsonify(commons.trueReturn(data, '已进行后台处理'))


@_main.route('/data_module/upload_images/<collection_id>', methods=['POST'])
@user_required
def upload_images(collection_id):
    """
    上传图片 检测/分割
    """
    local_time = time.time()

    collection = user_identification(collection_id, g.user.id)  # 当前集合
    if not collection:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '不存在的数据集'))

    if 2 != collection.type:
        return jsonify(commons.falseReturn(RET.DATAERR, '', '请选择正确的数据集类型进行上传'))

    upload_image_site = request.files.getlist('upload_image_site')  # 图片文件
    label_file = request.files.getlist('label_file')  # 标注文件
    table_site = request.files.get('table_site')  # 对应表文件

    if not upload_image_site:
        return jsonify(commons.falseReturn(RET.PARAMERR, '', '缺少图片文件'))

    # if len(upload_image_site) > 100:
    # return jsonify(commons.falseReturn(RET.PARAMERR, '当前已选图片{}张'.format(len(upload_image_site)), '超过图片最大限制100'))

    image_dict = {}
    for i in upload_image_site:
        image_dict[i.filename] = base64.b64encode(i.read())

    label_dict = {}
    if label_file:
        for x in label_file:
            label_dict[x.filename] = base64.b64encode(x.read())

    if table_site:
        table_site = table_site.read()
    from DataSet.celery_tasks.tasks import detection
    detection.delay(table_site, image_dict, label_dict, collection_id)

    try:
        request_id = request.cookies.get('session')[:36]
    except TypeError:
        request_id = {}
    time_used = int((time.time() * 1000) - int(local_time * 1000))
    data = {'dataset_id': collection.id, 'request_id': request_id, 'time_used': time_used}
    return jsonify(commons.trueReturn(data, '已进行后台处理'))


@_main.route('/data_module/delete_dataset', methods=['DELETE'])
@user_required
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
    from DataSet.celery_tasks.tasks import delete_set
    delete_set.delay(g.user.id, name)

    try:
        request_id = request.cookies.get('session')[:36]
    except TypeError:
        request_id = {}
    time_used = int((time.time() * 1000) - int(local_time * 1000))

    return jsonify(err_no=RET.OK, err_desc='OK',
                   request_id=request_id, time_used=time_used
                   )


@_main.route('/data_module/list_dataset', methods=['GET'])
def get_index():
    """
    数据集--列表
    :return:
    """
    local_time = time.time()
    result = auth.identify(request)
    if 0 == result['err_no'] and result['data']:
        try:
            user = User.query.filter_by(id=result['data']).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(commons.falseReturn(RET.DBERR, '', '查询数据库错误'))

        # try:
        #     collection = redis_store.get('my_collection_%s' % user.id)
        # except Exception as e:
        #     current_app.logger.error(e)
        #     collection = None
        # if collection:
        #     return jsonify(commons.trueReturn(collection, "OK"))

        try:
            collection = user.collections
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(commons.falseReturn(RET.DBERR, '', '查询数据集信息异常'))
        if not collection:
            return jsonify(commons.falseReturn(RET.NODATA, '', '无数据集信息'))
        my_list = []
        for i in collection:
            my_list.append(i.to_dict())
        my_json = json.dumps(my_list)
        # try:
        #     redis_store.setex('my_collection_%s' % user.id, 7200, my_json)
        # except Exception as e:
        #     current_app.logger.error(e)

        try:
            request_id = request.cookies.get('session')[:36]
        except TypeError:
            request_id = {}
        time_used = int((time.time() * 1000) - int(local_time * 1000))

        resp = {"time_used": time_used, "request_id": request_id, "collections": json.loads(my_json)}
        return jsonify(commons.trueReturn(resp, "OK"))
    else:
        return jsonify(result)


@_main.route('/data_module/<int:collection_id>', methods=['GET'])
def collection_info(collection_id):
    """
    数据集--详情
    :return:
    """
    local_time = time.time()
    result = auth.identify(request)
    if 0 == result['err_no'] and result['data']:
        collection = user_identification(collection_id, result['data'])
        if not collection:
            return jsonify(commons.falseReturn(RET.DBERR, '', '不存在的数据集'))
        # try:
        #     ret = redis_store.get('data_info_%s' % collection_id)
        # except Exception as e:
        #     current_app.logger.error(e)
        #     ret = None
        # if ret:
        #     current_app.logger.info('hit redis personage detail info')
        #     return '{"err_no":"0","err_desc":"OK","data":%s}' % ret

        try:
            collection_data = collection.to_dict()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(commons.falseReturn(RET.DBERR, '', 'The query fails'))

        collection_data['images'] = len(collection.images)
        versions = {}
        average_number = 0
        width = 0
        height = 0
        if collection.versions:
            for i in collection.versions:
                if 2 == collection.type:
                    versions[i.name] = {"count": len(i.images), "average_number": i.average_number,
                                        "mean_size": i.mean_size}
                    average_number += i.average_number
                    width += float(str(i.mean_size).split('*')[0])
                    height += float(str(i.mean_size).split('*')[1])
                else:
                    versions[i.name] = {"count": len(i.images)}
            if 2 == collection.type:
                collection_data.update(versions=versions, average_number=average_number,
                                       mean_size="{}*{}".format(width / len(collection.versions),
                                                                height / len(collection.versions))
                                       )
            else:
                collection_data['versions'] = versions
        label = Label.query.filter_by(collection_id=collection_id).all()
        labels = {}
        if label:
            collection_data['label_num'] = len(label)
            for i in label:
                labels[int(i.label_id)] = [i.name, i.count]
            collection_data['labels'] = labels
        collection_json = json.dumps(collection_data)
        # try:
        #     redis_store.setex('data_info_%s' % collection_id, 7200, collection_json)
        # except Exception as e:
        #     current_app.logger.error(e)
        try:
            request_id = request.cookies.get('session')[:36]
        except TypeError:
            request_id = {}
        time_used = int((time.time() * 1000) - int(local_time * 1000))
        resp = {"time_used": time_used, "request_id": request_id, "collections": json.loads(collection_json)}
        return jsonify(commons.trueReturn(resp, "OK"))
    else:
        return jsonify(result)
