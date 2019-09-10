# -*- coding:utf-8 -*-
import cStringIO
import urllib2
from flask import request, json
# from DataSet.rabbitMQ.task_queue_client import *
from DataSet.rabbitMQ.image_post import image_recognition
from DataSet.fastdfs.view import fun
from DataSet.rabbitMQ.img_detection_recognition import image_recognition
from DataSet.rabbitMQ.img_detection_recognition import image_detection
from DataSet.api_0_1.test_a import _test_1


@_test_1.route('/test1', methods=['GET'])
def test():
    label_path = 'http://192.168.65.129:8888/group1/M00/00/00/wKhBgVuSPzWAEU7eAAAAwB-XEnY94.json'
    file = urllib2.urlopen(label_path)
    tmpIm = cStringIO.StringIO(file.read())
    print(tmpIm)
    a = tmpIm.read()
    print(type(a))
    print(a)
    a_ = json.loads(a)
    print(type(a_))
    print(a_)
    print(a_['classification'])
    return 'ok'


@_test_1.route('/test2', methods=['POST'])
def rabbitmq_test():
    from DataSet.rabbitMQ.task_queue_client import preprocessing_quantitative_clean_task
    collection_id = request.get_json().get('collection_id')
    print(collection_id)
    print(type(collection_id))
    preprocessing_quantitative_clean_task.delay(str(collection_id))
    return "ok"


# @test_1.route('/test4', methods=['POST'])
# def rabbitmq_test2():
#     collection_id = request.get_json().get('collection_id')
#     preprocessing_timed_clean_task.delay(str(collection_id))
#     return 'ok'
#
# @test_1.route('/test3', methods=['GET'])
# def image_post_test():
#     return image_recognition(2)
#
# @_test_1.route('/spider_test', methods=['GET'])
# def spider_test():
#     spider_list = list()
#     spider_list.append('金')
#     spider_list.append(1)
#     spider_list.append(1)
#     print(spider_list)
#
#     spider_task.delay(json.dumps(spider_list))
#     return 'ok'
#
# @test_1.route('/label_get_test', methods=['GET'])
# def label_get():
#     label_path = 'M00/00/00/wKhBgVuSPzWAEU7eAAAAwB-XEnY94.json'
#     a = fun.getInfo(label_path)
#     print(a)
#     return 'ok'
#
# @test_1.route('/rm_label_json_file', methods=['GET'])
# def rm_json():
#     file_name ='M00/00/00/wKhBgVuaC7iAPHWYAAAA8CiugSI95.json'
#     fun.remove(file_name)
#     return 'ok'
#
#
# @test_1.route('/recognition', methods=['GET'])
# def image():
#     # collection_id = 1
#     # label_name_list = ['person']
#     # preprocessing_task(collection_id, 1, label_name_list)
#     image_id = 12
#
#
#     return  image_detection(image_id)
@_test_1.route('/test3', methods=['POST'])
def version():
    from DataSet.rabbitMQ.task_queue_client import create_version_task
    data = request.get_json()
    collection_id = data['collection_id']
    name = data['name']
    image_count = 0
    old_version = 1
    create_version_task.delay(str(collection_id), name, image_count, old_version)
    return 'ok'

# s = "[u'/home/maxu/fastDFS/storage0/data/00/00/wKhBgVtr5ASAZ5SlAAAfRVsaYIU321.jpg', u'/home/maxu/fastDFS/storage0/data/00/00/wKhBgVtxOpyAKRyqAAD1mH6S1v4438.jpg']"
# b = s.strip('[]')
# a = b.split(',')
# print(a)
# print(b)


# for i in b:
#     print(i[:39])
#     a.append(i[:39])
# print(a)
#
# print(s)

# from PIL import Image
# from imutils import paths
# import imagehash
#
# imgDir = [u'/home/maxu/fastDFS/storage0/data/00/00/wKhBgVtr5ASAZ5SlAAAfRVsaYIU321.jpg', u'/home/maxu/fastDFS/storage0/data/00/00/wKhBgVtqlqqAXmP_AAAfRVsaYIU553.jpg']
#
# if __name__ == '__main__':
#
#     hashList = list()
#     imgList = list()
#     for imagePath in imgDir:
#         print(imagePath)
#         HASH = imagehash.dhash(Image.open(imagePath))
#         imgList.append(imagePath)
#
#         hashList.append(HASH)
#
#     for idx in range(0, len(hashList)):
#         H1 = hashList[idx]
#         for idx2 in range(idx + 1, len(hashList)):
#             H2 = hashList[idx2]
#             if abs(H1 - H2) <= 1:
#                 print('duplicated image found:\t', imgList[idx], imgList[idx2], ':\t', abs(H1 - H2))
# a = ['1','2','1,','1.']
#
# for i in range(len(a)):
#     print(i,'i')
#     print(a)
#     for m in range(i+1, len(a)):
#         print(m,'m')
#         del a[0]
#         print(a)
# b = 'qwqwqwq%s'
# a = '% c'
# c = '123'
# d = '%s%s%s' % (a,b,c)
# # strlist = [b,a]
# # d = ''.join(strlist)
# print(d)

# test_str = "[['/home/maxu/fastDFS/storage0/data/00/00/wKhBgVtr5ASAZ5SlAAAfRVsaYIU321.jpg', '/home/maxu/fastDFS/storage0/data/00/00/wKhBgVtxOpyAKRyqAAD1mH6S1v4438.jpg', '/home/maxu/fastDFS/storage0/data/00/00/wKhBgVtqlqqAXmP_AAAfRVsaYIU553.jpg', '/home/maxu/fastDFS/storage0/data/00/00/wKhBgVtqlNqAVRmcAAAfRVsaYIU187.jpg'], ['/home/maxu/fastDFS/storage0/data/00/00/wKhBgVtqlNqAVRmcAAAfRVsaYIU187.jpg', '/home/maxu/fastDFS/storage0/data/00/00/wKhBgVtqlqqAXmP_AAAfRVsaYIU553.jpg']]"
# a = test_str.strip('[[')
# a = a.strip(']]')
# a = a.replace("'",'')
# a = a.split('], [')
# b = a[0]
# b = b.split(', ')
# print(a)
# print(b)
#
# a = '192.168.65.129:8888/group1/M00/00/00/wKhBgVuSPzWARWN2AAFdc1Sh97s045.jpg'
#
# b = a.split('/',2)[2]
# print(b)
