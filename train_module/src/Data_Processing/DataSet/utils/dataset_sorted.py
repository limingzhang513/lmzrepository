# !/usr/bin/python2
# -*- coding:utf-8 -*-

import os
import json
import shutil
from pathlib2 import Path
from .mq_send import train_task_send


def json2sorted(img_path, train_data_path, test_data_path, ds_flag, req_data):
    """
    sort image according to the json file
    :param img_path:user's data-img dir
    :param train_data_path:user's train data dir
    :param test_data_path:user's test data dir
    :param ds_flag:train/test flag 1 -> train 2 -> test
    :param req_data: args of train request
    :return:a path which is user's data sorted (str)
    """
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
    for i in range(len(class_keys)):
        class_image_dict[i] = class_image_dict.pop(class_keys[i])
    if ds_flag == 1:
        make_sorted_dir(class_image_dict, train_data_path)
        move_img_2_sorted_dir(class_image_dict, train_data_path)
        train_task_send(req_data)
    else:
        make_sorted_dir(class_image_dict, test_data_path)
        move_img_2_sorted_dir(class_image_dict, test_data_path)


def make_sorted_dir(class_dict, data_path):
    """make sorted dir"""
    all_class_dir = []
    for name in class_dict.keys():
        _path = os.path.join(data_path, str(name))
        if not os.path.exists(_path):
            os.mkdir(_path)
            all_class_dir.append(_path)


def move_img_2_sorted_dir(class_dir, sorted_path):
    """move image file to sorted dir"""
    for i, v in class_dir.items():
        new_path = os.path.join(sorted_path, str(i))
        for old_path in v:
            img_file = os.path.basename(old_path)
            new_img_file = os.path.join(new_path, img_file)
            if not os.path.exists(new_img_file):
                shutil.move(old_path, new_path)


