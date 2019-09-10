# -*- coding:utf-8 -*-
from DataSet.api_0_1.image_detection_recognition import _img
from flask import request, current_app, jsonify, json
from DataSet.models import Label, Collection
from DataSet.utils.serial_code import RET
from DataSet.api_0_1.image_detection_recognition.image_detection_result import image_detection_result_list, \
    image_recognition_result_list
from multiprocessing import Pool
import time
import sched


@_img.route('/image_preprocessing/<collection_id>', methods=['GET'])
def preprocessing(collection_id):  # 图像预处理
    """预标注页面"""
    labels_list = list()
    try:
        labels = Label.query.filter_by(collection_id=collection_id).all()  # 查询collection_id对应的所有的label
    except Exception as e:
        current_app.logger.error(e)  # flask 自带的日志记录模块
        return jsonify(err_no=RET.DBERR, err_desc='查询失败')
    for label in labels:
        labels_list.append(label.name)
    # 用户选择的检测功能后台
    try:
        collection = Collection.query.filter_by(id=collection_id).first()  # 通过collection_id匹配一个符合条件的collection
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(err_no=RET.DBERR, err_desc='查询失败')
    model = collection.type  # 默认是 1
    # 根据用户选则的模型类返回的能识别的标签

    preprocessing_label = []  # 预处理标签
    if model == 1:
        # preprocessing_label = image_recognition_result_list
        for l in image_recognition_result_list:
            preprocessing_label = preprocessing_label + l  #
    else:
        # preprocessing_label = image_detection_result_list
        for l in image_detection_result_list:
            preprocessing_label = preprocessing_label + l

    return jsonify(err_no=RET.OK, err_desc='ok', label=labels_list, model=model,
                   preprocessing_label=preprocessing_label)


@_img.route('/image_preprocessing_set', methods=['POST'])
def preprocessing_set():
    """预标注功能"""
    data = request.get_json()
    collection_id = data['collection_id']
    label_name = data['label_name']
    c_label_name = data['correspondent_label_name']  # 通讯标签名？？？

    try:
        label = Label.query.filter_by(collection_id=collection_id, name=label_name).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(err_no=RET.DBERR, err_desc='查询失败')
    if label is None:
        return jsonify(err_no=RET.DBERR, err_desc='没有此标签')
    try:
        collection = Collection.query.filter_by(id=collection_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(err_no=RET.DBERR, err_desc='查询失败')
    model = collection.type

    # data_list = list()
    # data_list.append(label_name)
    # data_list.append(c_label_name)
    # data_list.append(model)
    # data_list.append(pre_model_id)

    # with open('./preprocessing.json', 'r') as f:
    # a = f.read()
    # a = json.loads(a)
    # a[str(collection_id)] = data_list
    # a = json.dumps(a)
    # with open('./preprocessing.json', 'w') as f:
    # f.write(a)
    label_list = []
    if model == 1:
        label_list = image_recognition_result_list  # 图像识别结果集
    elif model == 2:
        label_list = image_detection_result_list  # 图像检测结果集

    pre_model_id = -1
    c_label_name = str(c_label_name[0])
    for idx, labels in enumerate(label_list):
        if c_label_name in labels:
            pre_model_id = idx
            break
    if pre_model_id == -1:
        return jsonify(err_no=RET.DBERR, err_desc='没有此标签')

    with open(
            '/home/duduo_data/China-Mobile/Data_Processing/DataSet/api_0_1/image_detection_recognition/preprocessing.json',
            'r') as f:
        a = f.read()
        a = json.loads(a)
        collection_id_s = str(collection_id)
        pre_model_key = '%d_%d' % (model, pre_model_id)
        if collection_id_s in a.keys():
            if pre_model_key in a[collection_id_s]:
                a[collection_id_s][pre_model_key][c_label_name] = label_name
            else:
                a[collection_id_s][pre_model_key] = {c_label_name: label_name}
        else:
            a[collection_id_s] = {pre_model_key: {c_label_name: label_name}}

        a = json.dumps(a)
        with open(
                '/home/duduo_data/China-Mobile/Data_Processing/DataSet/api_0_1/image_detection_recognition/preprocessing.json',
                'w') as f:
            f.write(a)

    return jsonify(err_no=RET.OK, err_desc='配置成功')


@_img.route('/file_read/<n>', methods=['GET'])
def file_read(n):
    from DataSet.celery_tasks.tasks import preprocessing as preprocessing_t
    with open(
            '/home/duduo_data/China-Mobile/Data_Processing/DataSet/api_0_1/image_detection_recognition/preprocessing.json',
            'r') as f:
        file_data = f.read()
        file_data = json.loads(file_data)
        if len(file_data) > 0:  # file_data长度表示存在多少个属性
            p = Pool(len(file_data))  # 多少属性进程池存储多少进程
            for key in file_data:
                label_info = file_data[key]
                p.apply_async(preprocessing_t, args=(int(key), label_info))
                # p.apply_async(preprocessing_t, args=(key, value))
            p.close()
            p.join()
    # s.enter(15, 2, file_read, (n))
    # s.run()
    return 'ok'


s = sched.scheduler(time.time, time.sleep)
