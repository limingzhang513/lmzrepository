# !/usr/bin/python2
# -*- coding:utf-8 -*-

import caffe
import numpy as np


def proto2npy(proto_path):
    mean_npy_path = '/home/cy/workspace/cmcc/China-Mobile/Data_Processing/tests/caffe_classification/1_abc/sorted/caffeNet_mean.npy'
    blob = caffe.proto.caffe_pb2.BlobProto()
    data = open(proto_path, 'rb').read()
    blob.ParseFromString(data)
    array = np.array(caffe.io.blobproto_to_array(blob))
    mean_npy = array[0]
    np.save(mean_npy_path, mean_npy)


proto_path = '/home/cy/workspace/cmcc/China-Mobile/Data_Processing/tests/caffe_classification/1_abc/sorted/imagenet_mean.binaryproto'
proto2npy(proto_path)
