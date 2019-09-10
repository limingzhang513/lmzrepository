# !/usr/bin/python2
# -*- coding:utf-8 -*-

import os
import datetime
from flask import request, jsonify, current_app, url_for, g
from werkzeug.utils import secure_filename
from .. import api
from DataSet import db
from DataSet.utils.serial_code import RET
from DataSet.models.modelsModel import Models
from DataSet.utils.auth_decorator import login_required


@api.route('/api/create_model', methods=['POST'])
@login_required
def new_model():
    """
    create a new model
    :return:
    """
    is_default = request.json.get('default_id')
    if is_default:
        model = Models.from_json_default(request.json)
    else:
        model = Models.from_json(request.json)
    if model is None:
        return jsonify(err_no=RET.PARAMERR, err_desc=u'参数错误')
    model.user_id = g.user_id
    db.session.add(model)
    db.session.flush()
    mid = model.id
    db.session.commit()
    return jsonify(err_no=RET.OK, err_desc='OK', mid=mid)


@api.route('/api/del_models', methods=['POST'])
@login_required
def del_model():
    """
    delete a existing model
    :return:
    """
    if not request.json.get('mids'):
        return jsonify(err_no=RET.PARAMERR, err_desc=u'缺少参数')
    for mid in request.json['mids']:
        model = Models.query.filter_by(id=mid).first()
        if model is None:
            return jsonify(err_no=RET.NODATA, err_desc=u'该数据不存在')
        if g.user_id != model.user_id:
            return jsonify(err_no=RET.ROLEERR, err_desc=u'用户身份不匹配')
        db.session.delete(model)
        db.session.commit()
    return jsonify(err_no=RET.OK, err_desc='OK')


@api.route('/api/get_models/')
@login_required
def get_models():
    """
    get all of models as a list
    :return:
    """
    page = request.args.get('page', 1, type=int)
    pagination = Models.query.filter_by(user_id=g.user_id).paginate(page,
                                       per_page=current_app.config['MODELS_TASKS_PER_PAGE'],
                                       error_out=False)
    models = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_models', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_models', page=page+1)
    return jsonify({
        'err_no': RET.OK,
        'err_desc': 'OK',
        'models': [model.to_dict() for model in models],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/api/model_detail', methods=['POST'])
@login_required
def get_model():
    """
    get the detail of a model
    :return:
    """
    mid = request.json.get('mid')
    if not mid:
        return jsonify(err_no=RET.PARAMERR, err_desc=u'缺少参数')
    model = Models.query.filter_by(id=mid, user_id=g.user_id).first()
    if model is None:
        return jsonify(err_no=RET.DATAERR, err_desc=u'模型不存在')
    return jsonify(err_no=RET.OK, err_desc='OK', model_detail=model.to_dict())


@api.route('/api/get_default', methods=['POST'])
#@login_required
def default_models():
    """
    get the default models which is qualified
    :return:
    """
    model_frame = request.json.get('frame')
    model_type = request.json.get('type')
    if not model_frame or not model_type:
        return jsonify(err_no=RET.PARAMERR, err_desc=u'缺少参数')
    models = Models.query.filter_by(frame=model_frame, type=model_type, is_default=True)
    if models is None:
        return jsonify(err_no=RET.NODATA, err_desc=u'无预制数据')
    return jsonify({
        'err_no': RET.OK,
        'err_desc': 'OK',
        'default_models': [model.to_default_dict() for model in models]
    })


@api.route('/api/upload_define', methods=['POST'])
@login_required
def upload_model_define():
    """
    upload a model define file
    :return:
    """
    if 'file' not in request.files:
        return jsonify(err_no=RET.PARAMERR, err_desc=u'上传参数错误')
    file = request.files['file']
    if file.filename == '':
        return jsonify(err_no=RET.NODATA, err_desc=u'无有效文件上传')
    if file and allowed_file(file.filename):
        filename = str(g.user_id) + '-' + str(datetime.datetime.now()) + '-' + \
                   secure_filename(file.filename)
        upload_path = os.path.join(current_app.config['BASE_FOLDER'], 'DataSet/static/custom_model/define/')
        save_path = os.path.join(upload_path, filename)
        file.save(save_path)
        return jsonify(err_no=RET.OK, err_desc=u'模型定义上传成功', defain_path=save_path)
    return jsonify(err_no=RET.ROLEERR, err_desc=u'定义文件格式错误')


@api.route('/api/upload_weight', methods=['POST'])
@login_required
def upload_model_weight():
    """
    upload a model weight file
    :return:
    """
    if 'file' not in request.files:
        return jsonify(err_no=RET.PARAMERR, err_desc=u'上传参数错误')
    file = request.files['file']
    if file.filename == '':
        return jsonify(err_no=RET.NODATA, err_desc=u'无有效文件上传')
    if file and allowed_file(file.filename):
        filename = str(g.user_id) + '-' + str(datetime.datetime.now()) + '-' + \
                   secure_filename(file.filename)
        upload_path = os.path.join(current_app.config['BASE_FOLDER'], 'DataSet/static/custom_model/weight/')
        save_path = os.path.join(upload_path, filename)
        file.save(save_path)
        return jsonify(err_no=RET.OK, err_desc=u'权重文件上传成功', weight_path=save_path)
    return jsonify(err_no=RET.ROLEERR, err_desc=u'权重文件格式错误')


def allowed_file(filename):
    """
    is the upload-file allowed?
    :param filename: filename
    :return: True or False
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

