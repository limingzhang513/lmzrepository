# !/usr/bin/python2
# -*- coding:utf-8 -*-

import os
import json
import shutil
import commands
from pathlib2 import Path
from DataSet import celery, db
from DataSet.models.tasksModel import Tasks
from DataSet.models.datasetModel import Dataset
from DataSet.utils.download_unzip import downloader, unzip, make_dir, get_weight_path
from DataSet.utils.dataset_sorted import make_sorted_dir, move_img_2_sorted_dir
from .mq_send import train_task_send


@celery.task
def download2txt(ds_id, var_id, headers, user_id, user_dir, task_id, req=None, data=None, ds_flag=1):
    if ds_flag == 1:
        inner_par = ['max_iter', 'batch_size', 'optimizer', 'lr_policy', 'mirror', 'vertical_flip', 'scale',
                     'mean', 'test_interval', 'base_lr', 'gamma', 'power', 'stepvalue', 'stepsize']
        par = dict()
        for item in inner_par:
            if item in req:
                par[item] = req[item]
        data['parameter'] = par
        weight_name = req.get('weight_name')
        if (weight_name is not None) and (weight_name != ''):
            model_path = get_weight_path(weight_name, data['model'])
        else:
            model_path = ''
        data['model_path'] = model_path
    try:
        dataset_obj = Dataset.query.filter_by(user_id=user_id, dataset_id=str(ds_id), dataset_var=str(var_id)).first()
        if dataset_obj and dataset_obj.dataset_path:
            _path_dict = json.loads(dataset_obj.dataset_path)
            zipfile_paths = list()
            for _, v in _path_dict.items():
                if os.path.exists(v):
                    zipfile_paths.append(str(v))
                else:
                    print 'dataset is not exists, please delete info from table'
                    zipfile_paths = downloader(ds_id=ds_id, var_id=var_id, headers=headers,
                                               user_id=user_id, ds_flag=ds_flag, user_dir=user_dir)
                    zipfile_dict = dict()
                    for i in range(len(zipfile_paths)):
                        zipfile_dict.update({i: zipfile_paths[i]})
                    zip_files = json.dumps(zipfile_dict)
                    ds_obj = Dataset(user_id=user_id, dataset_id=ds_id, dataset_var=str(var_id), dataset_path=zip_files)
                    db.session.add(ds_obj)
                    db.session.commit()
        else:
            zipfile_paths = downloader(ds_id=ds_id, var_id=var_id, headers=headers,
                                  user_id=user_id, ds_flag=ds_flag, user_dir=user_dir)
            zipfile_dict = dict()
            for i in range(len(zipfile_paths)):
                zipfile_dict.update({i: zipfile_paths[i]})
            zip_files = json.dumps(zipfile_dict)
            ds_obj = Dataset(user_id=user_id, dataset_id=ds_id, dataset_var=str(var_id), dataset_path=zip_files)
            db.session.add(ds_obj)
            db.session.commit()
    except Exception as e:
        print e
        task = Tasks.query.filter_by(id=task_id).first()
        task.state = u'训练异常'
        db.session.add(task)
        db.session.commit()
        return None
    print 'Start unzip data'
    img_path = unzip(zipfile_paths, user_dir, ds_flag)
    print 'Unzip complete'
    train_data_path, val_data_path = make_dir(user_dir)
    print 'Start sort data and create txt'
    data_sorted(img_path, user_dir,  train_data_path, val_data_path, ds_flag, data)
    print 'create txt file complete'
    task = Tasks.query.filter_by(id=task_id).first()
    db.session.add(task)
    task.train_dataset_path = train_data_path
    task.test_dataset_path = val_data_path
    db.session.commit()
    print user_dir


def data_sorted(img_path, user_dir, train_data_path, val_data_path, ds_flag, req_data):
    json_path = Path(img_path)
    all_json_file = list(json_path.glob('**/*.json'))
    class_image_dict = {}
    for json_file in all_json_file:
        with json_file.open() as f:
            json_string = json.load(f)
        class_name = json_string['classification'][0]['category_name']
        img_file = json_string['images']['file_name']
        if class_name not in class_image_dict:
            class_image_dict[class_name] = [os.path.join(img_path, img_file)]
        else:
            class_image_dict[class_name].append(os.path.join(img_path, img_file))
    class_keys = class_image_dict.keys()
    class_num = len(class_keys)
    if ds_flag == 1:
        req_data['parameter'].update({'num_output': class_num})
    for i in range(class_num):
        class_image_dict[i] = class_image_dict.pop(class_keys[i])
    if ds_flag == 1:
        make_sorted_dir(class_image_dict, train_data_path)
        move_img_2_sorted_dir(class_image_dict, train_data_path)
        create_txt(class_image_dict, user_dir, ds_flag)
        create_db(user_dir, train_data_path + '/', ds_flag)
        if 'mean' not in req_data['parameter']:
            image_mean_path = create_image_mean(user_dir)
            req_data['parameter'].update({'mean_file_path': image_mean_path})
        req_data['parameter'] = set_default_par(req_data['parameter'])
        train_task_send(req_data)

    else:
        move_val_img(class_image_dict, val_data_path)
        create_txt(class_image_dict, user_dir, ds_flag)
        create_db(user_dir, val_data_path + '/', ds_flag)


def move_val_img(class_image_dict, val_data_path):
    for _, v in class_image_dict.items():
        for old_path in v:
            img_name = os.path.basename(old_path)
            new_path = os.path.join(val_data_path, img_name)
            if not os.path.exists(new_path):
                shutil.move(old_path, new_path)


def create_txt(class_image_dict, user_dir, ds_flag):
    if ds_flag == 1:
        txt_path = os.path.join(user_dir, 'sorted/train.txt')
    else:
        txt_path = os.path.join(user_dir, 'sorted/val.txt')
    if not os.path.exists(txt_path):
        for k, v in class_image_dict.items():
            for img in v:
                img_name = img.split('/')[-1]
                if ds_flag == 1:
                    img_path = os.path.join(str(k) + '/', img_name)
                else:
                    img_path = img_name
                with open(txt_path, 'a+') as fp:
                    fp.write(img_path + ' ' + str(k) + '\n')


def create_db(user_dir, images_path, ds_flag):
    caffe_root = '/home/cy/softyu/caffe'
    if ds_flag == 1:
        lmdb_name = 'train_lmdb'
        txt_save_path = os.path.join(user_dir, 'sorted', 'train.txt')
    else:
        lmdb_name = 'val_lmdb'
        txt_save_path = os.path.join(user_dir, 'sorted', 'val.txt')
    lmdb_save_path = os.path.join(user_dir, 'sorted', lmdb_name)
    convert_imageset_path = os.path.join(caffe_root, 'build/tools/convert_imageset')
    cmd = """%s --shuffle --resize_height=64 --resize_width=64 %s %s %s"""
    status, output = commands.getstatusoutput(cmd % (convert_imageset_path, images_path,
                                                     txt_save_path, lmdb_save_path))
    print output
    if status == 0:
        print "%s - lmbd file is created" % str(ds_flag)


def create_image_mean(user_dir):
    compute_image_mean_path = '/home/cy/softyu/caffe/build/tools/compute_image_mean'
    sorted_path = os.path.join(user_dir, 'sorted')
    train_lmdb_path = os.path.join(sorted_path, 'train_lmdb')
    image_mean_path = os.path.join(sorted_path, 'imagenet_mean.binaryproto')
    cmd = """%s %s %s"""
    status, output = commands.getstatusoutput(cmd % (compute_image_mean_path, train_lmdb_path, image_mean_path))
    print output
    if status == 0:
        print "mean file is created"
    return image_mean_path


def set_default_par(par_dict):
    new_par = {}
    for k, v in par_dict.items():
        if v == '' or v is None:
            continue
        new_par.update({k: v})
    new_par.setdefault('test_iter', '10')
    new_par.setdefault('test_interval', '200')
    new_par.setdefault('base_lr', '0.01')
    new_par.setdefault('momentum', '0.9')
    new_par.setdefault('display', '10')
    new_par.setdefault('weight_decay', '0.0005')
    policy = new_par.setdefault('lr_policy', 'fixed')
    if policy != 'fixed':
        new_par.setdefault('gamma', '0.1')
    new_par.setdefault('max_iter', '2000')
    new_par.setdefault('snapshot', '1000')
    new_par.setdefault('batch_size', '8')
    new_par.setdefault('stepsize', '1000')
    new_par.setdefault('optimizer', 0)
    return new_par
