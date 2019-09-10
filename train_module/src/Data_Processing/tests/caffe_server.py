# !/usr/bin/python2
# -*- coding:utf-8 -*-

import os
import json
from flask_httpauth import HTTPBasicAuth
from flask import Flask, request, jsonify
from caffe_classification import train, modify_net, create_solver


auth = HTTPBasicAuth
app = Flask(__name__)


@app.route('/caffe_training', methods=['POST'])
def caffe_train():
    data = json.loads(request.data)
    task_id = data.get('task_id')
    trained_dir = data.get('trained_path')
    print '*-*req is coming:%s*-*' % task_id
    print '*-*trained_dir:%s*-*' % trained_dir
    try:
        user_dir = data['user_dir']
        model_path = data['model_path']
        train_data_path = os.path.join(user_dir, 'sorted', 'train_lmdb')
        val_data_path = os.path.join(user_dir, 'sorted', 'val_lmdb')
        par = data['parameter']
        if data['model'] == 'vgg16':
            if 'mean_file_path' in par.keys():
                modify_net.fix_vgg_net(user_dir=user_dir, train_data_path=train_data_path, val_data_path=val_data_path,
                                       par=par, mean_file_path=par['mean_file_path'])
            else:
                modify_net.fix_vgg_net(user_dir=user_dir, train_data_path=train_data_path, val_data_path=val_data_path,
                                       par=par, mean_value=par['mean_value'])
        elif data['model'] == 'resnet50':
            if 'mean_file_path' in par.keys():
                modify_net.fix_resnet(user_dir=user_dir, train_data_path=train_data_path, val_data_path=val_data_path,
                                       par=par, mean_file_path=par['mean_file_path'])
            else:
                modify_net.fix_resnet(user_dir=user_dir, train_data_path=train_data_path, val_data_path=val_data_path,
                                       par=par, mean_value=par['mean_value'])
        else:
            print '不支持该模型'
        create_solver.write_solver(user_dir=user_dir, trained_dir=trained_dir, model=data['model'], par=par)
        train.caffe_train(user_dir=user_dir, trained_path=trained_dir, model=data['model'], par=par, model_path=model_path)
        print '*-*all of complete:%s*-*' % task_id
    except Exception as e:
        print e
        print '*-*err stop:%s*-*' % task_id
    return jsonify({'state': True})


if __name__ == '__main__':
    app.run(port=5003)
