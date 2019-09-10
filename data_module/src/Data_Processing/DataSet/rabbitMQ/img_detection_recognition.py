# -*- coding:utf-8 -*-
from flask import json
import requests
from PIL import Image as image_pil
from io import BytesIO
import base64
import cStringIO
import urllib2


# from DataSet.models import Image
# from DataSet.fastdfs.view import fun

# n = [ b64, model, pre_model ]
def image_recognition(n):
    """单张本地图像识别"""
    # 拼接post请求
    results = dict()
    b64 = n[0]
    for pre_model in n[2]:
        if pre_model == 0:
            url = 'http://192.168.66.58/api/ad_image_recognition'
            datas = {'image': b64,
                     'object': '1',
                     'scene': '1',
                     'logo': '0'}
            response = requests.post(url, data=datas)
            json_data = response.json()
            # json_data= json.dumps(json_data)
            results[pre_model] = json_data
    return json.dumps(results)


def image_detection(n):
    """单张图像检测"""
    results = dict()
    b64 = n[0]
    for pre_model in n[2]:
        if pre_model == 0:
            url = 'http://192.168.66.58/detect/single_image'
            datas = {'function': '100',
                     'image': b64}
            response = requests.post(url, data=datas)
            json_data = response.json()
            w = json_data['Width']
            h = json_data['Height']
            for idx, d in enumerate(json_data['detection']):
                json_data['detection']['xmin'] = float(d['xmin']) * w
                json_data['detection']['xmax'] = float(d['xmax']) * w
                json_data['detection']['ymin'] = float(d['ymin']) * h
                json_data['detection']['ymax'] = float(d['ymax']) * h
                json_data['detection']['pre_model'] = pre_model

            results[pre_model] = json_data
        elif pre_model == 1:
            url = 'http://218.206.177.147:6666/cmri/restful/faceAnalysis/extraFeatures'
            datas = json.dumps({'base64Pic': str(b64).encode('utf-8')})
            response = requests.post(url, data=datas)
            try:
                json_data = response.json()
            except:
                break
            # print( '[preprocessing_task]', json_data )

            refmt_data = dict()
            refmt_data['detection'] = list()
            for d in json_data['data']:
                res = dict()
                res['score'] = '1'
                res['label_id'] = 0  # face
                res['xmin'] = '%.02f' % (d['bbox'][0])
                res['ymin'] = '%.02f' % (d['bbox'][1])
                res['xmax'] = '%.02f' % (d['bbox'][2])
                res['ymax'] = '%.02f' % (d['bbox'][3])
                res['feaData'] = d['feaData']
                res['pre_model'] = pre_model

                refmt_data['detection'].append(res)
            results[pre_model] = refmt_data
    return json.dumps(results)
