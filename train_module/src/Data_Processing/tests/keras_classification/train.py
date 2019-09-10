#!/usr/bin/python3
# -*- coding:utf-8 -*-

import numpy as np
import os
from . import config
from . import util
np.random.seed(1337)  # for reproducibility


def init():
    util.set_img_format()
    util.override_keras_directory_iterator_next()
    util.set_classes_from_train_dir()
    util.set_samples_info()

    if util.get_keras_backend_name() != 'theano':
        util.tf_allow_growth()

    if not os.path.exists(config.trained_dir):
        os.mkdir(config.trained_dir)


def train(epoch, batch_size, model_path=None):
    if model_path:
        model = util.get_model_from_h5file(
            class_weight=util.get_class_weight(config.train_dir),
            nb_epoch=epoch,
            batch_size=batch_size,
            model_path=model_path,
            freeze_layers_number=None)
    else:
        model = util.get_model_class_instance(
            class_weight=util.get_class_weight(config.train_dir),
            nb_epoch=epoch,
            batch_size=batch_size,
            freeze_layers_number=None)
    model.train()
    print('Training is finished!')

