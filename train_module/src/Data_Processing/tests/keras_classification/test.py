#!/usr/bin/env python
import os
import glob
import tarfile
import numpy as np
from scipy.io import loadmat
from shutil import copyfile, rmtree
import sys
import config

data_path = 'data'

image_labels_path = os.path.join(data_path, 'imagelabels.mat')

setid_path = os.path.join(data_path, 'setid.mat')

setid = loadmat(setid_path)

idx_train = setid['trnid'][0] - 1
idx_test = setid['tstid'][0] - 1
idx_valid = setid['valid'][0] - 1

image_labels = loadmat(image_labels_path)['labels'][0]

image_labels -= 1

# image_labels = list(set(image_labels))

files = sorted(glob.glob(os.path.join(data_path, 'jpg', '*.jpg')))

labels = np.array([i for i in zip(files, image_labels)])


def move_files(dir_name, labels):
    # cur_dir_path = os.path.join(config.data_dir, dir_name)
    # if not os.path.exists(cur_dir_path):
    #     os.mkdir(cur_dir_path)

    # for i in range(0, 102):
    #     class_dir = os.path.join(config.data_dir, dir_name, str(i))
    #     os.mkdir(class_dir)

    print labels
    # for label in labels:
    #     src = str(label[0])
    #     dst = os.path.join(cwd, config.data_dir, dir_name, label[1], src.split(os.sep)[-1])
    #     copyfile(src, dst)

# print setid
# print 'idx_train: ', idx_train
# print 'idx_test: ', idx_test
# print 'idx_valid: ', idx_valid
# print 'image_labels: ', image_labels
# print 'files: ', files
# print 'labels: ', labels
# print '*' * 100
# move_files('train', labels[6733])


import importlib

module = importlib.import_module("models.vgg16")

model = module.inst_class()
print model
model.train()