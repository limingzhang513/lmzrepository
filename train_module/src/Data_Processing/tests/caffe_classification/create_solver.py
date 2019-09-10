# !/usr/bin/python2
# -*- coding:utf-8 -*-

import os


def write_solver(user_dir, trained_dir, model, par):
    print 'create solver file'
    sp = dict()
    if str(model) == 'vgg16':
        solver_file = os.path.join(user_dir, 'vgg16solver.prototxt')
        sp['net'] = "".join(['"', os.path.join(str(user_dir), 'vgg16net_train_val.prototxt'), '"'])
    else:
        solver_file = os.path.join(user_dir, 'resnet50solver.prototxt')
        sp['net'] = "".join(['"', os.path.join(str(user_dir), 'resnet50_train_val.prototxt'), '"'])
    sp['test_iter'] = str(par['test_iter'])
    sp['test_interval'] = str(par['test_interval'])
    sp['base_lr'] = str(par['base_lr'])
    sp['momentum'] = str(par['momentum'])
    sp['weight_decay'] = str(par['weight_decay'])
    sp['stepsize'] = '1000'
    if par['lr_policy'] == 0:
        sp['lr_policy'] = "".join(['"', 'fixed', '"'])
    elif par['lr_policy'] == 1:
        sp['lr_policy'] = "".join(['"', 'step', '"'])
        sp['gamma'] = str(par['gamma'])
    else:
        sp['lr_policy'] = "".join(['"', 'fixed', '"'])
    sp['display'] = str(par['display'])
    sp['max_iter'] = str(par['max_iter'])
    sp['snapshot'] = '1000'
    sp['snapshot_prefix'] = "".join(['"', os.path.join(str(trained_dir), 'trained'), '"'])
    sp['solver_mode'] = 'GPU'
    with open(solver_file, 'w') as f:
        for key, value in sorted(sp.items()):
            if not (type(value) is str):
                raise TypeError('All solver parameters must be strings')
            f.write('%s: %s\n' % (key, value))
        print 'solver file is created'
