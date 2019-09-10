# -*- coding:utf-8 -*-
import urllib
import httplib
import requests
from DataSet.models import Image as image
from PIL import Image
from io import BytesIO
import base64


def image_recognition(image_id):
    """单张本地图像识别"""
    # img_path = image.query.filter_by(id=image_id).first()
    img_path = '/home/maxu/Desktop/test_a/test_image/2018072618035014307.gif'
    img = Image.open(img_path)

    mode = 'RGB'

    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new(mode, img.size)
        background.paste(img)
        img = background

    bs = BytesIO()
    img.save(bs, format="JPEG")

    b64 = base64.b64encode(bs.getvalue())

    url = 'http://192.168.66.58/api/ad_image_recognition'
    datas = '{"image":"%s",\n'\
             '"object":"1",\n'\
             '"scene":"1",\n'\
             '"logo":"0"}' % b64
    response = requests.post(url, data=datas)
    json = response.json()
    print(response)
    return json


def image_detection(image_id):
    """单张图像检测"""
    img_path = image.query.filter_by(id=image_id).first()
    img = Image.open(img_path)

    mode = 'RGB'

    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new(mode, img.size)
        background.paste(img)
        img = background

    bs = BytesIO()
    img.save(bs, format="JPEG")

    b64 = base64.b64encode(bs.getvalue())

    url = 'http://192.168.66.58/detect/single_image'
    datas = {'function':'100',
             'image':b64}
    response = requests.post(url, data=datas)
    json = response.json()
    return json

if __name__ == '__main__':
    image_detection()
    image_recognition(2)