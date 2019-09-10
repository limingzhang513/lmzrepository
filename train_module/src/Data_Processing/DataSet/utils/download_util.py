# !/usr/bin/python2
# -*- coding:utf-8 -*-

import os
import glob
import time
import zipfile
import requests
from flask import current_app
from DataSet.models.resultModel import TrainResult


def downloader(ds_id, var_id, headers, user_id, ds_flag, user_dir):
    """
    a data downloader
    :param ds_id: dataset id (int)
    :param var_id: version id (list)
    :param headers: request headers
    :param user_id: user id
    :param ds_flag: 1: train, 2: val
    :param user_dir: user dir
    :return: the path of zip file
    """
    start = time.time()
    chunk_size = 4096
    zipfile_paths = list()
    for var in var_id:
        payload = {'collection_id': ds_id, 'version_id': var}
        header = {'Content-Type': 'application/json'}
        if headers:
            header.update({'Authorization': str(headers)})
        try:
            r = requests.get(url=current_app.config['DOWNLOAD_DS_URL'], headers=header, params=payload, stream=True)
        except ValueError:
            return 404
        if r is None:
            return None
        if ds_flag == 1:
            zip_path = os.path.join(user_dir, ''.join([str(user_id), '_', str(var), '_train', '.zip']))
        else:
            zip_path = os.path.join(user_dir, ''.join([str(user_id), '_', str(var), '_test', '.zip']))
        if r.status_code == 200:
            with open(zip_path, 'wb') as file:
                for data in r.iter_content(chunk_size=chunk_size):
                    file.write(data)
        end = time.time()
        print '\n' + 'Download complete, the time is%.2fs' % (end - start)
        zipfile_paths.append(zip_path)
    return zipfile_paths


def unzip(zipfile_paths, unzip_path, ds_flag):
    """unzip zip file"""
    img_path = None
    try:
        for zip_path in zipfile_paths:
            print type(zip_path)
            zip_file = zipfile.ZipFile(zip_path)
            for names in zip_file.namelist():
                if ds_flag == 1:
                    zip_file.extract(names, unzip_path + '/train_jpg')
                    img_path = unzip_path + '/train_jpg'
                else:
                    zip_file.extract(names, unzip_path + '/val_jpg')
                    img_path = unzip_path + '/val_jpg'
            zip_file.close()
    except Exception as e:
        print e
        return None
    return img_path


def make_dir(user_dir):
    """make sorted dirs"""
    sorted_path = os.path.join(user_dir, 'sorted')
    train_data_path = os.path.join(sorted_path, 'train')
    test_data_path = os.path.join(sorted_path, 'val')
    try:
        if not os.path.exists(sorted_path):
            os.mkdir(sorted_path)
        if not os.path.exists(train_data_path):
            os.mkdir(train_data_path)
        if not os.path.exists(test_data_path):
            os.mkdir(test_data_path)
    except OSError as e:
        print e
    return train_data_path, test_data_path


def get_weight_path(weight_name, model_define):
    """
    get weight file path
    :param weight_name: weight name
    :return: weight path
    """
    if weight_name is not None:
        task_id, task_frame = weight_name.split('_')[0:2]
        trained_obj = TrainResult.query.filter_by(task_id=task_id).first()
        if not trained_obj:
            return ''
        trained_path = trained_obj.trained_path
        if task_frame == '1':
            weight_path = glob.glob(trained_path + '/model-*.h5')[0]
        else:
            weights = glob.glob(trained_path + '/*.caffemodel')
            sort_list = []
            for path in weights:
                _name, _ = os.path.splitext(path)
                sort_list.append(_name.split('_')[-1])
            if str(model_define) == 'vgg16':
                weight_path = os.path.join(trained_path, 'vgg16solver_iter_%s.caffemodel' % sort_list[0])
            else:
                weight_path = os.path.join(trained_path, 'resnet50solver_iter_%s.caffemodel' % sort_list[0])
        return weight_path

