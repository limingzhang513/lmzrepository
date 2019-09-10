# !/usr/bin/python2
# coding=utf-8

import os
import json
import requests
from celery_worker import app
from DataSet import db
from DataSet.models.tasksModel import Tasks
from DataSet.models.resultModel import TrainResult


def dl_req(req_data):
    """
    start a train task
    :param req_data: parameter
    :return:
    """
    try:
        db.init_app(app)
        data = json.loads(req_data)
        task = Tasks.query.filter_by(id=data['task_id']).first()
        if data['frame'] == 1:
            url = 'http://127.0.0.1:5002/training'
        else:
            url = 'http://127.0.0.1:5003/caffe_training'
        r = requests.post(url=url, data=req_data)
        if r.status_code != 200:
            for i in range(1, 4):
                print '训练任务检测到status: %s, 进行第 %s 次重试...' % (r.status_code, i)
                reconn = requests.post(url=url, data=req_data)
                if reconn.status_code == 200:
                    break
                elif i == 3:
                    task.state = u'训练出错，请调整参数'
                    db.session.add(task)
                    db.session.commit()
                    # server.log
                    raise ValueError
        par = del_par(data['parameter'])
        task.parameter = json.dumps(par)
        task.state = u'已完成'
        db.session.add(task)
        db.session.commit()
        plt_path = os.path.join(data['trained_path'], 'plt_img')
        trained_path = os.path.join(data['trained_path'], 'trained')
        result = TrainResult(user_id=data.get('user_id'), model_id=data.get('model_id'), task_id=data.get('task_id'),
                             plt_path=plt_path, trained_path=trained_path)
        db.session.add(result)
        db.session.commit()
    except Exception as e:
        print e
        print '训练过程出错'
        result = TrainResult(user_id=data.get('user_id'), model_id=data.get('model_id'), task_id=data.get('task_id'))
        db.session.add(result)
        db.session.commit()


def del_par(par_dict):
    if 'test_interval' in par_dict:
        del par_dict['test_interval']
    if 'momentum' in par_dict:
        del par_dict['momentum']
    if 'display' in par_dict:
        del par_dict['display']
    if 'weight_decay' in par_dict:
        del par_dict['weight_decay']
    if 'snapshot' in par_dict:
        del par_dict['snapshot']
    if 'mean_value' in par_dict:
        del par_dict['mean_value']
    if 'mean_file_path' in par_dict:
        del par_dict['mean_file_path']
    return par_dict






