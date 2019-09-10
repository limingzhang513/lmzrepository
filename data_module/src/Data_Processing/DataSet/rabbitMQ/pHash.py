# -*- coding: utf-8 -*-
from PIL import Image
import imagehash
from flask import json
import cStringIO, urllib2


def clean(imgDir):
    hashList = list()
    imgList = list()
    delete_imglist = list()  # 需要删除的imagePath

    for imagePath in imgDir:
        # for imagePath in s:
        #     print(imagePath)
        file = urllib2.urlopen(imagePath)
        tmpIm = cStringIO.StringIO(file.read())
        HASH = imagehash.dhash(Image.open(tmpIm))
        imgList.append(imagePath)
        # print(imgList)
        hashList.append(HASH)
        # print(hashList)

    for idx in range(0, len(hashList)):
        H1 = hashList[idx]
        for idx2 in range(idx + 1, len(hashList)):
            H2 = hashList[idx2]
            if abs(H1 - H2) <= 1:
                print('duplicated image found:\t', imgList[idx], imgList[idx2], ':\t', abs(H1 - H2))
                delete_imglist.append(imgList[idx2])
    delete_imglist = list(set(delete_imglist))
    response_image_list = list()
    response_image_list.append(imgList)
    response_image_list.append(delete_imglist)

    response_image_list = json.dumps(response_image_list)
    return response_image_list
