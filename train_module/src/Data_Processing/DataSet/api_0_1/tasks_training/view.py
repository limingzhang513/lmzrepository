# !/usr/bin/python2
# -*- coding:utf-8 -*-

import os
import glob
import uuid
import base64
import requests
import datetime
from werkzeug.utils import secure_filename
from flask import request, jsonify, current_app, url_for, g, send_from_directory
from .. import api
from DataSet import db
from DataSet.utils.serial_code import RET
from DataSet.models.tasksModel import Tasks
from DataSet.models.modelsModel import Models
from DataSet.models.datasetModel import Dataset
from DataSet.models.resultModel import TrainResult
from DataSet.utils.download_unzip import download2processing
from DataSet.utils.download_to_db import download2txt
from DataSet.utils.auth_decorator import login_required


@api.route('/api/create_task', methods=['POST'])
@login_required
def new_task():
    """
    create a new task
    :return:
    """
    model = Models.query.filter_by(id=request.json.get('model_id')).first()
    if model is None:
        return jsonify(err_no=RET.NODATA, err_desc=u'模型不存在')
    task = Tasks.from_json(request.json, model.frame)
    if task is None:
        return jsonify(err_no=RET.PARAMERR, err_desc=u'参数错误')
    user_id = g.user_id
    task.user_id = user_id
    db.session.add(task)
    db.session.flush()
    task_id = task.id
    db.session.commit()
    user_dir, trained_path = make_dir(user_id)
    train_data_path = os.path.join(user_dir, 'sorted', 'train')
    val_data_path = os.path.join(user_dir, 'sorted', 'val')
    try:
        token = request.headers['Authorization']
    except KeyError:
        return jsonify(err_no=RET.DATAERR, err_desc=u'缺少用户身份信息')
    try:
        # keras_request
        if model.frame == 1:
            data = {'task_id': task_id, 'model_id': request.json.get('model_id'), 'user_id': user_id,
                    'model': model.define_path, 'train_dir': train_data_path, 'val_dir': val_data_path,
                    'trained_path': trained_path, 'frame': 1}
            download2processing.delay(ds_id=request.json.get('test_dataset_id'),
                                      var_id=request.json.get('test_var_ids'),
                                      headers=token, user_id=user_id, task_id=task_id, ds_flag=2, user_dir=user_dir)
            download2processing.delay(ds_id=request.json.get('train_dataset_id'),
                                      var_id=request.json.get('train_var_ids'),
                                      headers=token, user_id=user_id, task_id=task_id,
                                      user_dir=user_dir, req=request.json, data=data)
        # caffe_request
        elif model.frame == 2:
            data = {'task_id': task_id, 'model_id': request.json.get('model_id'), 'model': model.define_path,
                    'user_id': user_id, 'user_dir': user_dir, 'trained_path': trained_path, 'frame': 2}
            download2txt.delay(ds_id=request.json.get('test_dataset_id'), var_id=request.json.get('test_var_ids'),
                               headers=token, user_id=user_id, task_id=task_id, ds_flag=2, user_dir=user_dir)
            download2txt.delay(ds_id=request.json.get('train_dataset_id'), var_id=request.json.get('train_var_ids'),
                               headers=token, user_id=user_id, task_id=task_id, user_dir=user_dir,
                               req=request.json, data=data)
        else:
            return jsonify(err_no=RET.DATAERR, err_desc=u'获取框架类型错误')
    except:
        return jsonify(err_no=RET.DATAERR, err_desc=u'数据集获取失败')
    return jsonify(err_no=RET.OK, err_desc='OK', tid=task_id)


@api.route('/api/del_tasks', methods=['POST'])
@login_required
def del_task():
    """
    delete a existing train task
    :return:
    """
    if not request.json['tids']:
        return jsonify(err_no=RET.PARAMERR, err_desc=u'参数错误')
    for tid in request.json['tids']:
        task = Tasks.query.filter_by(id=tid).first()
        if task is None:
            return jsonify(err_no=RET.NODATA, err_desc=u'该数据不存在')
        if g.user_id != task.user_id:
            return jsonify(err_no=RET.ROLEERR, err_desc=u'用户身份不匹配')
        db.session.delete(task)
        db.session.commit()
        return jsonify(err_no=RET.OK, err_desc='OK')


@api.route('/api/get_tasks/')
@login_required
def get_tasks():
    """
    get all of train tasks as a list
    :return:
    """
    page = request.args.get('page', 1, type=int)
    pagination = Tasks.query.filter_by(user_id=g.user_id).paginate(page,
                                                                   per_page=current_app.config['MODELS_TASKS_PER_PAGE'],
                                                                   error_out=False)
    tasks = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_tasks', page=page - 1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_tasks', page=page + 1)
    return jsonify({
        'err_no': RET.OK,
        'err_desc': 'OK',
        'tasks': [task.to_dict() for task in tasks],
        'prev': prev,
        'next': next,
        'count': pagination.total})


@api.route('/api/task_detail', methods=['POST'])
@login_required
def get_task():
    """
    get the detail of a train task
    :return:
    """
    tid = request.json.get('tid')
    if not tid:
        return jsonify(err_no=RET.PARAMERR, err_desc=u'缺少参数')
    task = Tasks.query.filter_by(id=tid, user_id=g.user_id).first()
    if task is None:
        return jsonify(err_no=RET.DATAERR, err_desc=u'任务不存在')
    plt_result = TrainResult.query.filter_by(task_id=tid, user_id=g.user_id).first()
    task_detail = task.to_dict_detail()
    model_name = Models.query.filter_by(id=task.model_id).first().name
    task_detail.update({'model_name': model_name})
    plt_base64_list = []
    if plt_result is not None:
        plt_base64_list = get_plt_base64_list(plt_result.plt_path)
    task_detail.update({"result": plt_base64_list})
    return jsonify(err_no=RET.OK, err_desc='OK', task_detail=task_detail)


@api.route('/api/get_dataset/')
@login_required
def get_dataset():
    """
    get datasets
    :return:
    """
    try:
        headers = request.headers
        r = requests.get(url=current_app.config['GET_DATASET_URL'], headers=headers)
        r.encoding = 'utf-8'
        return jsonify(err_no=RET.OK, err_desc='OK', train_datasets=r.json())
    except Exception:
        return jsonify(err_no=RET.NODATA, err_desc=u'获取数据集错误')


@api.route('/api/get_versions', methods=['POST'])
@login_required
def get_version():
    """
    get dataset versions
    :return:
    """
    try:
        ds_id = request.json.get('collection_id')
        if ds_id is None:
            return jsonify(err_no=RET.DATAERR, err_desc=u'缺少数据集id')
        headers = request.headers
        r = requests.get(url=current_app.config['GET_VERSION_URL'].format(int(ds_id)), headers=headers)
        r.encoding = 'utf-8'
        if 'data' in r.json() and 'versions_name' in r.json().get('data'):
            return jsonify(err_no=RET.OK, err_desc='OK', versions_name=r.json().get('data').get('versions_name'))
        elif 'err_desc' in r.json():
            return jsonify(err_no=r.json().get('err_no'), err_desc=r.json().get('err_desc'), versions_name={})
    except Exception:
        return jsonify(err_no=RET.NODATA, err_desc=u'获取版本错误')


@api.route('/api/get_weight', methods=['POST'])
@login_required
def get_weight():
    """
    get per-training weight
    :return:
    """
    model_id = request.json.get('model_id')
    if model_id is None:
        return jsonify(err_no=RET.DATAERR, err_desc=u'缺少模型id')
    model_frame = str(Models.query.filter_by(id=model_id).first().frame)
    weight_name_list = []
    weight_obj = TrainResult.query.filter_by(user_id=g.user_id, model_id=model_id)
    if weight_obj:
        for obj in weight_obj:
            trained_path = obj.trained_path
            if trained_path:
                try:
                    if model_frame not in ['1', '2']:
                        return jsonify(err_no=RET.DATAERR, err_desc=u'不支持该模型')
                    elif model_frame == '1':
                        _ = glob.glob(obj.trained_path + '/model-*.h5')[0]
                    else:
                        _ = glob.glob(obj.trained_path + '/*.caffemodel')[0]
                except IndexError:
                    continue
                _task = Tasks.query.filter_by(id=obj.task_id).first()
                weight_name = ''.join([str(obj.id), '_', model_frame, '_', _task.name])
                weight_name_list.append(weight_name)
    return jsonify(err_no=RET.OK, err_desc='OK', weight_names=weight_name_list)


@api.route('/api/tasks/parameter/', methods=['POST'])
@login_required
def upload_task():
    """
    upload train parameter
    :return:
    """
    if 'file' not in request.files:
        return jsonify(err_no=RET.PARAMERR, err_desc=u'上传参数错误')
    file = request.files['file']
    if file.filename == '':
        return jsonify(err_no=RET.NODATA, err_desc=u'无有效文件上传')
    if file and allowed_file(file.filename):
        filename = str(g.user_id) + '-' + 'parameter' + '-' + str(datetime.datetime.now()) + '-' + \
                   secure_filename(file.filename)
        upload_path = os.path.join(current_app.config['BASE_FOLDER'], 'DataSet/static/parameter_task/parameter/')
        file.save(os.path.join(upload_path, filename))
        return jsonify(err_no=RET.OK, err_desc=u'超参数上传成功', filename=filename, filepath=upload_path)
    return jsonify(err_no=RET.ROLEERR, err_desc=u'文件格式错误')


@api.route('/api/download_log', methods=['POST'])
@login_required
def download_log():
    """
    download task training server.log
    :return:
    """
    task_id = request.json.get('task_id')
    if not task_id:
        return jsonify({'msg': u'缺少task_id'})
    res_obj = TrainResult.query.filter_by(user_id=g.user_id, task_id=task_id).first()
    if res_obj:
        log_path = res_obj.log_path
        if log_path:
            if os.path.exists(log_path):
                file_dir, file_name = os.path.split(log_path)
                return send_from_directory(file_dir, file_name, as_attachment=True)
        else:
            return jsonify({'msg': u'日志文件不存在'})


@api.route('/api/update_log_info', methods=['POST'])
def update_log_info():
    """
    update log info
    :return:
    """
    try:
        _path = request.json.get('_path')
        log_path = request.json.get('log_path')
        if _path is None or log_path is None:
            return None
        update_obj = TrainResult.query.filter_by(trained_path=os.path.join(_path, 'trained')).first()
        if update_obj:
            if update_obj.log_path is None:
                update_obj.log_path = log_path
                db.session.add(update_obj)
                db.session.commit()
    except Exception:
        print u'日志更新失败'
    return jsonify(err_no=RET.OK, err_desc='OK')


@api.route('/api/del_expire_info', methods=['POST'])
def del_expire_info():
    """
    del expire info
    :return:
    """
    try:
        flag = request.json.get('flag')
        if flag is None or flag not in [1, 2]:
            return None
        if flag == 1:
            Dataset.check_expire()
        if flag == 2:
            TrainResult.check_expire()
    except Exception:
        print u'删除过期对象失败'
    return jsonify(err_no=RET.OK, err_desc='OK')


def allowed_file(filename):
    """
    determine the file ext
    :param filename: a filename
    :return:
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def make_dir(user_id):
    """
    make dirs
    :param user_id: user's id
    :return:
    """
    dl_path = os.path.join(current_app.config['BASE_FOLDER'], 'DataSet/static/datasets/')
    user_dir = os.path.join(dl_path, str(user_id) + '_' + str(uuid.uuid1()))
    os.mkdir(user_dir)
    rt_path = os.path.join(current_app.config['BASE_FOLDER'], 'DataSet/static/train_result/')
    trained_path = os.path.join(rt_path, user_dir.split('/')[-1])
    os.mkdir(trained_path)
    os.mkdir(trained_path + '/trained')
    os.mkdir(trained_path + '/plt_img')
    os.mkdir(trained_path + '/log')
    return user_dir, trained_path


def get_plt_base64_list(plt_path):
    """
    get plt result path , join the img path and transform jpg to base64
    :param plt_path:
    :return:a img-base64 list
    """
    if plt_path is not None:
        img_path_list = glob.glob(plt_path + '/*.jpg')
        plt_base64_list = []
        for img_path in img_path_list:
            with open(img_path, "rb") as f:
                base64_data = base64.b64encode(f.read())
            plt_base64_list.append(base64_data)
        return plt_base64_list
    return []
