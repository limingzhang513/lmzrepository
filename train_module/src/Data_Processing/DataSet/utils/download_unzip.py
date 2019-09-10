# !/usr/bin/python2
# -*- coding:utf-8 -*-

import os
import json
from DataSet import celery, db
from DataSet.models.tasksModel import Tasks
from DataSet.models.datasetModel import Dataset
from DataSet.utils.download_util import downloader, unzip, make_dir, get_weight_path
from DataSet.utils.dataset_sorted import json2sorted


@celery.task
def download2processing(ds_id, var_id, headers, user_id, task_id, user_dir, req=None, data=None, ds_flag=1):
    """
    a asynchronous task, auto download data and transform the data into sorted dataset can be used
    :param ds_id: dataset id (int)
    :param var_id: version id (list)
    :param headers: request headers
    :param user_id: user id (int)
    :param task_id: task id (int)
    :param user_dir: user's data path (str)
    :param ds_flag: train == 1 or test == 2 (int)
    :param req_data: args of train request
    :return: a path which is user's data sorted (str)
    """
    if ds_flag == 1:
        inner_par = ['epoch', 'batch_size', 'optimizer', 'lr_policy', 'mirror', 'vertical_flip', 'scale', 'mean']
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
    print 'Start unzip dataset'
    img_path = unzip(zipfile_paths, user_dir, ds_flag)
    if img_path is None:
        raise ValueError
    print 'Unzip complete'
    train_data_path, test_data_path = make_dir(user_dir)
    print 'Start sort data'
    json2sorted(img_path, train_data_path, test_data_path, ds_flag, data)
    task = Tasks.query.filter_by(id=task_id).first()
    db.session.add(task)
    task.train_dataset_path = train_data_path
    task.test_dataset_path = test_data_path
    db.session.commit()
    print 'Data processing is finished'
    return train_data_path, test_data_path








