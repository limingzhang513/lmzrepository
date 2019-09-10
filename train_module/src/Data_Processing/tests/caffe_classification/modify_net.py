# !/usr/bin/python2
# -*- coding:utf-8 -*-

import os
import caffe.proto.caffe_pb2 as caffe_pb2
import google.protobuf.text_format as text_format


def fix_vgg_net(user_dir, train_data_path, val_data_path, par, mean_file_path=None, mean_value=None):
    net = caffe_pb2.NetParameter()
    user_net_path = os.path.join(user_dir, 'vgg16net_train_val.prototxt')
    with open('/home/cy/workspace/cmcc/China-Mobile/'
              'Data_Processing/tests/caffe_classification/'
              'vggnet_train_val.prototxt', 'r') as f:
        text_format.Merge(f.read(), net)
    print 'modify VGGnet parm'
    if ('mirror' in par) and (str(par['mirror']) == '1'):
        net.layer[0].data_param.mirror = True
    if mean_file_path is not None:
        net.layer[0].transform_param.mean_file = mean_file_path
    else:
        net.layer[0].transform_param.mean_value.extend(mean_value)
    net.layer[0].data_param.source = train_data_path
    net.layer[0].data_param.batch_size = par['batch_size']
    net.layer[1].data_param.source = val_data_path
    net.layer[1].data_param.batch_size = par['batch_size']
    net.layer[-3].inner_product_param.num_output = par['num_output']

    with open(user_net_path, 'w') as f:
        f.write(text_format.MessageToString(net))
    print 'net parm is changed'
    return True


def fix_resnet(user_dir, train_data_path, val_data_path, par, mean_file_path=None, mean_value=None):
    net = caffe_pb2.NetParameter()
    user_net_path = os.path.join(user_dir, 'resnet50_train_val.prototxt')
    with open('/home/cy/workspace/cmcc/China-Mobile/'
              'Data_Processing/tests/caffe_classification/'
              'train_resnet50.prototxt', 'r') as f:
        text_format.Merge(f.read(), net)
    print 'modify Resnet parm'
    if ('mirror' in par) and (str(par['mirror']) == '1'):
        net.layer[0].data_param.mirror = True
    if mean_file_path is not None:
        net.layer[0].transform_param.mean_file = mean_file_path
        net.layer[1].transform_param.mean_file = mean_file_path
    else:
        net.layer[0].transform_param.mean_value.extend(mean_value)
        net.layer[1].transform_param.mean_value.extend(mean_value)
    net.layer[0].data_param.source = train_data_path
    net.layer[0].data_param.batch_size = par['batch_size']
    net.layer[1].data_param.source = val_data_path
    net.layer[1].data_param.batch_size = par['batch_size']
    net.layer[-3].name = ''.join(['fc', str(par['num_output'])])
    net.layer[-3].inner_product_param.num_output = par['num_output']

    with open(user_net_path, 'w') as f:
        f.write(text_format.MessageToString(net))
    print 'net parm is changed'
    return True
