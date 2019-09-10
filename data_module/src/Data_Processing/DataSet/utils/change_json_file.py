# -*- coding:utf-8 -*-

from flask import json
from DataSet import db
from DataSet.fastdfs.view import fun
from DataSet.models import Image, Label


def storage(up_file, collection, file_name):
    try:
        image_status = fun.upload(up_file, file_ext_name='jpg')
        image = Image()
        image.name = file_name
        image.site = image_status.get('file_id')
        image.collection_id = collection.id
        db.session.add(image)
        db.session.commit()
    except Exception as e:
        fun.remove(image_status['filename'])
        db.session.rollback()
        return '{"err_no": "1", "err_desc": "数据保存失败", "data": %s}' % e

    images = Image.query.filter_by(collection_id=collection.id, site=image_status['filename']).first()
    return images


class ChangeJsonFile(object):

    def __init__(self):
        self.join_images = '{' + '"images": {'
        self.join_images += '"data_uploaded": "%s",' + '"file_name": "%s",'
        self.join_images += '"height": "%s",' + '"width": "%s",' + '"id": %s},'
        self.json_label_dict = ["background", "person", "bicycle", "car", "motorcycle", "airplane", "bus",
                                "train", "truck", "boat", "traffic_light", "fire_hydrant", "stop_sign", "parking_meter",
                                "bench",
                                "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe",
                                "backpack",
                                "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports_ball",
                                "kite",
                                "baseball_bat", "baseball_glove", "skateboard", "surfboard", "tennis_racket", "bottle",
                                "wine_glass",
                                "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
                                "broccoli", "carrot",
                                "hot_dog", "pizza", "donut", "cake", "chair", "couch", "potted_plant", "bed",
                                "dining_table", "toilet",
                                "tv", "laptop", "mouse", "remote", "keyboard", "cell_phone", "microwave", "oven",
                                "toaster", "sink",
                                "refrigerator", "book", "clock", "vase", "scissors", "teddy_bear", "hair_drier",
                                "toothbrush"]

    def segmentation(self, images, size, file_name):
        str_data = file_name
        json_dict_data = json.loads(str_data)
        annotation = json_dict_data.get('annotation')
        data_list = []
        for i in annotation:
            category_id = i.get('category_id')  # 标签label_id
            try:
                label_name = self.json_label_dict[category_id]
                # print( label_name )
                labels = Label.query.filter_by(name=label_name, collection_id=images.collection_id).first()
            except:
                continue
            # labels = Label.query.filter_by(label_id=category_id, collection_id=images.collection_id).first()
            if not labels:
                continue
            a = '{"bbox": ' + str(i['bbox']) + ','
            a += '"category_id": ' + str(labels.label_id) + ',' + '"category_name": ' + '"{}"'.format(labels.name) + ','
            a += '"segmentation": [' + str(i['segmentation']) + ']}' + ','
            data_list.append(a)
        next_join = '"classification": ' + '[],'
        next_join += '"annotation": [' + ''.join(data_list)[:-1] + ']}'
        str_list = [self.join_images, next_join]
        data = ''.join(str_list)
        up_file = data % (images.create_time, images.site[10:], size.get('height'), size.get('width'), images.id)
        file_json = fun.upload(up_file, file_ext_name='json')
        images.status = 3
        images.label_path = file_json.get('file_id')
        db.session.add(images)
        db.session.commit()


cjf = ChangeJsonFile()
