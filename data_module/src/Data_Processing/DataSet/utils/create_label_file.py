# -*- coding:utf-8 -*-

import xml.dom.minidom
import cStringIO
from DataSet import db
from DataSet.fastdfs.view import fun
from DataSet.models import Label


def image_size(up_file):
    from PIL import Image
    tmpIm = cStringIO.StringIO(up_file)
    img = Image.open(tmpIm)

    size = {'width': img.size[0], 'height': img.size[1]}
    return size


class CreateLabelFile(object):
    """
    生成标记文件
    """

    def __init__(self):
        self.join_images = '{' + '"images": {'
        self.join_images += '"data_uploaded": "%s",' + '"file_name": "%s",'
        self.join_images += '"height": "%s",' + '"width": "%s",' + '"id": %s},'

    def segmentation(self, images, size, file_name, collection):  # collection_id
        """
        检测分割
        """
        ann_file = xml.dom.minidom.parseString(file_name)  # 打开xml文档

        annotation = ann_file.documentElement  # 得到xml文件对象

        obj_list = annotation.getElementsByTagName('object')  # 获取object标签对象
        segmented = annotation.getElementsByTagName('segmented')
        obj_cnt = 0
        ann_list = []
        segmentation = segmented[0].firstChild.data
        for idx in range(0, obj_list.length):
            # segmentation = segmented[objCnt].firstChild.data
            obj_cnt += 1
            name = obj_list[idx].getElementsByTagName("name")[0].childNodes[0].data  # 取出当前name标签对之间的数据
            bndbox = obj_list[idx].getElementsByTagName("bndbox")[0]
            xmin = bndbox.getElementsByTagName("xmin")[0].childNodes[0].data  # 下左
            xmax = bndbox.getElementsByTagName("xmax")[0].childNodes[0].data  # 下右
            ymin = bndbox.getElementsByTagName("ymin")[0].childNodes[0].data  # 上左
            ymax = bndbox.getElementsByTagName("ymax")[0].childNodes[0].data  # 上右
            labels = Label.query.filter_by(collection_id=collection.id, name=name).first()
            if not labels:
                continue
            # write anns in annStr
            ann_str = '{'
            ann_str += '"bbox": [' + xmin + ", " + ymin + ", " + \
                       str(int(xmax) - int(xmin)) + ', ' + str(int(ymax)-int(ymin)) + '], '
            ann_str += '"category_id": '+ str(labels.label_id) + ',' + '"category_name": ' + '"' +name+'"' + ','
            ann_str += '"segmentation": [' + "[" + str(segmentation) + "]" + "]" + "},"
            ann_list.append(ann_str)
        next_join = '"classification": ' + '[],'
        next_join += '"annotation": [' + ''.join(ann_list)[:-1] + ']}'
        str_list = [self.join_images, next_join]
        data = ''.join(str_list)
        #  '图片上传时间','xml文件'，宽高，图片id
        up_file = data % (images.create_time, images.site[10:], size.get('height'), size.get('width'), images.id)
        file_json = fun.upload(up_file, file_ext_name='json')
        images.status = 3
        images.label_path = file_json.get('file_id')
        db.session.add(images)
        db.session.commit()

    def default(self, images, size):
        """
        未标记
        """
        next_join = '"classification": [],'
        next_join += '"annotation": []' + '}'
        str_list = [self.join_images, next_join]
        data = ''.join(str_list)
        up_file = data % (images.create_time, images.site[10:], size.get('height'), size.get('width'), images.id)
        file_json = fun.upload(up_file, file_ext_name='json')
        images.status = 0
        images.label_path = file_json.get('file_id')
        db.session.add(images)
        db.session.commit()

    def classification(self, images, size, category_id, category_name):
        """
        分类/人脸识别
        """

        next_join = '"classification": [' + '{'
        next_join += '"category_id": %s,' + '"category_name": "%s"' + '}' + '],'
        next_join += '"annotation": []' + '}'

        strlist = [self.join_images, next_join]
        data = ''.join(strlist)
        up_file = data % (images.create_time, images.site[10:], size.get('height'), size.get('width'), images.id,
                          category_id, category_name)
        print 111
        print type(up_file)
        print up_file
        file_json = fun.upload(up_file, file_ext_name='json')
        print 222
        print file_json
        images.status = 3
        images.label_path = file_json.get('file_id')
        db.session.add(images)
        db.session.commit()


clf = CreateLabelFile()



