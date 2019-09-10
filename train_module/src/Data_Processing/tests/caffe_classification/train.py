# !/usr/bin/python2
# -*- coding:utf-8 -*-

import os
import numpy as np
import matplotlib.pyplot as plt
import caffe


def caffe_train(user_dir, trained_path, model, par, model_path):
    img_path = os.path.join(trained_path, 'plt_img', 'plt.jpg')
    if str(model) == 'vgg16':
        solver_file = os.path.join(str(user_dir), 'vgg16solver.prototxt')
    else:
        solver_file = os.path.join(str(user_dir), 'resnet50solver.prototxt')
    caffe.set_device(0)
    caffe.set_mode_gpu()
    if model_path == '':
        if par['optimizer'] == 0:
            print 'use SGD optimizer'
            solver = caffe.SGDSolver(solver_file)
        else:
            print 'use Adam optimizer'
            solver = caffe.AdamSolver(solver_file)
    else:
        try:
            print 'use pre-weight'
            solver = caffe.get_solver(solver_file)
            solver.net.copy_from(str(model_path))
        except:
            print '不支持该权重'

    niter = int(par['max_iter'])
    display = int(par['display'])
    test_iter = int(par['test_iter'])
    test_interval = int(par['test_interval'])

    train_loss = np.zeros(int(np.ceil(niter * 1.0 / display)))
    test_loss = np.zeros(int(np.ceil(niter * 1.0 / test_interval)))
    test_acc = np.zeros(int(np.ceil(niter * 1.0 / test_interval)))

    solver.step(1)
    _train_loss = 0
    _test_loss = 0
    _accuracy = 0

    for it in range(niter):
        # 每迭代一次，训练batch_size张图片
        solver.step(1)
        # train loss
        if str(model) == 'vgg16':
            _train_loss += solver.net.blobs['loss'].data
        else:
            _train_loss += solver.net.blobs['prob'].data
        if it % display == 0:
            # 平均train loss
            train_loss[it // display] = _train_loss / display
            _train_loss = 0

        if it % test_interval == 0:
            for test_it in range(test_iter):
                solver.test_nets[0].forward()
                # test loss
                if str(model) == 'vgg16':
                    _test_loss += solver.test_nets[0].blobs['loss'].data
                else:
                    _test_loss += solver.test_nets[0].blobs['prob'].data
                # test accuracy
                if str(model) == 'vgg16':
                    _accuracy += solver.test_nets[0].blobs['accuracy'].data
                else:
                    _accuracy += solver.test_nets[0].blobs['accuracy@1'].data
                # 平均test loss
            test_loss[it / test_interval] = _test_loss / test_iter
            # 平均test accuracy
            test_acc[it / test_interval] = _accuracy / test_iter
            _test_loss = 0
            _accuracy = 0

    print '\nplot the train loss and test accuracy\n'
    _, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    ax1.plot(test_interval * np.arange(len(test_loss)), test_loss, 'y')
    ax2.plot(test_interval * np.arange(len(test_acc)), test_acc, 'r')

    ax1.set_xlabel('iteration')
    ax1.set_ylabel('loss')
    ax2.set_ylabel('accuracy')
    plt.savefig(img_path)
    plt.close()
