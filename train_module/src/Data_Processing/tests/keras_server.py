# !/usr/bin/python3
# coding=utf-8

import json
import traceback
from flask_httpauth import HTTPBasicAuth
from flask import Flask, request, jsonify
from keras_classification import config, train, util

auth = HTTPBasicAuth()
app = Flask(__name__)


@app.route('/training', methods=['POST'])
def data_resize_training():
    """
    a machine learn server
    :return:
    """
    data = json.loads(request.data)
    task_id = data.get('task_id')
    print('*-*req is coming:%s*-*' % task_id)
    print('*-*trained_dir:%s*-*' % data.get('trained_path'))
    try:
        par = data.get('parameter')
        config.train_dir = data.get('train_dir')
        config.validation_dir = data.get('val_dir')
        config.plots_dir = data.get('trained_path') + '/plt_img'
        config.trained_dir = data.get('trained_path') + '/trained'
        config.model = data.get('model')
        if 'optimizer' in par:
            config.optimizer = par['optimizer']
        if 'lr_policy' in par:
            config.lr_policy = par['lr_policy']
        if 'horizontal_flip' in par:
            config.horizontal_flip = par['horizontal_flip']
        if 'vertical_flip' in par:
            config.vertical_flip = par['vertical_flip']
        if 'rescale' in par:
            config.rescale = par['rescale']
        if 'img_mean' in par and isinstance(par['img_mean'], list):
            config.img_mean = par['img_mean']
        if 'epoch' in par:
            config.epoch = par['epoch']
        if 'batch_size' in par:
            config.batch_size = par['batch_size']
        model_path = data.get('model_path')
        train.init()
        train.train(config.epoch, config.batch_size, model_path)
        util.clear_memory()
        print('*-*all of complete:%s*-*' % task_id)
        return jsonify({'state': True})
    except Exception as e:
        print(e)
        traceback.print_exc()
        print('*-*err stop:%s*-*' % task_id)


if __name__ == '__main__':
    app.run(port=5002)
