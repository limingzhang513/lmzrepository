# -*- coding:utf-8 -*-
import cStringIO
import urllib2
from DataSet.api_0_1.tagging import _tag
from DataSet.models import Image, Label, Collection
from flask import jsonify, current_app, request, json, render_template
from DataSet.utils.serial_code import RET
from DataSet.fastdfs.view import fun
from DataSet import db
from DataSet.utils.page_util import Pager
import math


@_tag.route('/tagging/ds_label/<collection_id>', methods=['GET'])
def show_label(collection_id):
    from sqlalchemy import and_
    """展示标签"""
    images_list = list()
    labels_list = list()
    labels_dict = dict()

    try:
        # images = Image.query.filter_by(collection_id=collection_id).all()  # 当前集合
        images = Image.query.filter(Image.collection_id == collection_id, Image.status < 3).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(err_no=RET.DBERR, err_desc='查询失败')
    try:
        labels = Label.query.filter_by(collection_id=collection_id).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(err_no=RET.DBERR, err_desc='查询失败')

    for image in images:
        images_dict = dict()

        show_image = current_app.config['NGINX_SITE'] + fun.getInfo(image.site)['group_file_id']
        images_dict['image'] = show_image

        label_url_path = current_app.config['NGINX_LABEL_SITE'] + fun.getInfo(image.label_path)['group_file_id']
        # 读取json文件内容
        file = urllib2.urlopen(label_url_path)
        tmpIm = cStringIO.StringIO(file.read())
        label_date = tmpIm.read()
        label_json_date = json.loads(label_date)

        images_dict['width'] = label_json_date['images']['width']
        images_dict['height'] = label_json_date['images']['height']
        images_dict['label_name'] = 'unknown'
        images_dict['label_id'] = -1
        images_dict['label'] = []

        if label_json_date['classification']:
            for i in label_json_date['classification']:
                images_dict['label_name'] = i['category_name']
                images_dict['label_id'] = i['category_id']
        if label_json_date['annotation']:
            image_labels_list = []
            for i in label_json_date['annotation']:
                label_dict = dict()
                num = i['bbox']
                a_list = list()
                for a in num:
                    b = float(a)
                    a_list.append(b)
                label_dict['bbox'] = a_list
                label_dict['label_name'] = i['category_name']
                label_dict['label_id'] = i['category_id']
                image_labels_list.append(label_dict)
            images_dict['label'] = image_labels_list
        images_list.append(images_dict)

    for label in labels:
        labels_dict[str(label.label_id)] = str(label.name)
    labels_list.append(labels_dict)

    return jsonify(err_no=RET.OK, err_desc='成功', image=images_list, label=labels_list)


@_tag.route('/tagging/save_label', methods=['POST'])
def save_label():
    """标注保存"""
    data = request.get_json()
    state = data.get('classification')
    collection_id = data.get('collection_id')
    collection_type = Collection.query.filter_by(id=collection_id).first().type
    # 分类/人脸识别标注
    if state:
        label_id = state['category_id']
        category_name = state['category_name']
        if category_name is not None:
            try:
                label = Label.query.filter_by(collection_id=collection_id, label_id=label_id).first()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(err_no=RET.DBERR, err_desc='查询失败')
            if not label:
                return jsonify(err_no=RET.NODATA, err_desc='没有该标签')
            # 创建要保存的标签字典
            classification = dict()
            classification['category_id'] = label_id
            classification['category_name'] = category_name

            image_site = data.get('image')

            try:
                image = Image.query.filter_by(site=str(image_site).split('/', 4)[4]).first()
            except:
                current_app.logger.error(image_site)
                return jsonify(err_no=RET.DBERR, err_desc='查询失败')

            if image.status == 3:
                return jsonify(err_no=RET.NODATA, err_desc='请勿重复标记分类图片')

            label_url_path = current_app.config['NGINX_SITE'] + fun.getInfo(image.label_path)['group_file_id']
            # 读取json文件内容
            file = urllib2.urlopen(label_url_path)
            tmpIm = cStringIO.StringIO(file.read())
            label_date = tmpIm.read()
            label_json_date = json.loads(label_date)
            label_json_date['classification'] = [classification]

            label_date = json.dumps(label_json_date)
            # 保存修改后的json文件
            new_label_path = fun.upload(label_date, file_ext_name='json')
            # 删除原json文件
            fun.remove(image.label_path)
            # 修改数据库json文件存储路径
            image.label_path = new_label_path['filename']
            # 修改图片状态
            if collection_type == 1:
                pass
                # image.status = 3
            label.count += 1
            db.session.commit()

        else:
            return jsonify(err_no=RET.PARAMERR, err_desc='参数缺失', )

    # 检测/分割标注
    state = data.get('annotation')
    if state:
        for label_dict in data.get('annotation'):
            category_id = label_dict['category_id']
            category_name = label_dict['category_name']
            bbox = label_dict['bbox']
            segmentation = label_dict['segmentation']
            if category_name and bbox is not None:
                try:
                    label = Label.query.filter_by(collection_id=collection_id, label_id=category_id).first()
                except Exception as e:
                    current_app.logger.error(e)
                    return jsonify(err_no=RET.DBERR, err_desc='查询失败')
                if not label:
                    return jsonify(err_no=RET.NODATA, err_desc='没有该标签')

                try:
                    for num in bbox:
                        num = float(num)
                        if math.isnan(num):
                            current_app.logger.error(num)
                            return jsonify(err_no=RET.DBERR, err_desc='参数错误')
                except Exception as e:
                    current_app.logger.error(e)
                    return jsonify(err_no=RET.DBERR, err_desc='参数错误')

                # 创建要保存的标签字典
                annotation = dict()
                annotation['bbox'] = bbox
                annotation['category_id'] = category_id
                annotation['category_name'] = category_name
                annotation['segmentation'] = segmentation
                image_site = data.get('image')
                image = Image.query.filter_by(site=str(image_site).split('/', 4)[4]).first()
                label_url_path = current_app.config['NGINX_SITE'] + fun.getInfo(image.label_path)['group_file_id']
                # 读取json文件内容
                file = urllib2.urlopen(label_url_path)
                tmpIm = cStringIO.StringIO(file.read())
                label_date = tmpIm.read()
                label_json_date = json.loads(label_date)

                label_json_date['annotation'].append(annotation)

                label_date = json.dumps(label_json_date)
                # 保存修改后的json文件
                new_label_path = fun.upload(label_date, file_ext_name='json')
                # 删除原json文件
                fun.remove(image.label_path)
                # 修改数据库json文件存储路径
                image.label_path = new_label_path['filename']
                # 修改图片状态
                if collection_type == 2:
                    pass
                    # image.status = 3
                label.count += 1
                db.session.commit()

            else:
                return jsonify(err_no=RET.PARAMERR, err_desc='参数缺失')

    return jsonify(err_no=RET.OK, err_desc='标注成功')


@_tag.route('/tagging/change_label', methods=['POST'])
def change_label():
    """改变标签"""
    data = request.get_json()
    state = data.get('classification')
    collection_id = data.get('collection_id')
    if state:
        label_id = state['category_id']
        category_name = state['category_name']
        if category_name is not None:
            try:
                label = Label.query.filter_by(collection_id=collection_id, label_id=label_id).first()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(err_no=RET.DBERR, err_desc='查询失败')
            if not label:
                return jsonify(err_no=RET.NODATA, err_desc='没有该标签')

            classification = dict()
            classification['category_id'] = label_id
            classification['category_name'] = category_name
            image_site = data.get('image')
            image = Image.query.filter_by(site=str(image_site).split('/', 4)[4]).first()

            label_url_path = current_app.config['NGINX_SITE'] + fun.getInfo(image.label_path)['group_file_id']
            # 读取json文件内容
            file = urllib2.urlopen(label_url_path)
            tmpIm = cStringIO.StringIO(file.read())
            label_date = tmpIm.read()
            label_json_date = json.loads(label_date)
            old_label_name = label_json_date['classification'][0]['category_name']
            old_label = Label.query.filter_by(collection_id=collection_id, name=old_label_name).first()
            old_label.count -= 1
            del label_json_date['classification'][0]
            label_json_date['classification'].append(classification)

            label_date = json.dumps(label_json_date)
            # 保存修改后的json文件
            new_label_path = fun.upload(label_date, file_ext_name='json')
            # 删除原json文件
            fun.remove(image.label_path)
            image.label_path = new_label_path['filename']

            label.count += 1
            db.session.commit()
        else:
            return jsonify(err_no=RET.PARAMERR, err_desc='参数缺失')

    # 检测/分割标注
    for label_dict in data.get('annotation'):
        category_id = label_dict['category_id']
        category_name = label_dict['category_name']
        print(label_dict)
        bbox = label_dict['bbox']
        old_bbox = label_dict['old_bbox']
        segmentation = label_dict['segmentation']
        if category_name and bbox and segmentation and old_bbox is not None:
            try:
                label = Label.query.filter_by(collection_id=collection_id, label_id=category_id).first()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(err_no=RET.DBERR, err_desc='查询失败')
            if not label:
                return jsonify(err_no=RET.NODATA, err_desc='没有该标签')

            try:
                for num in bbox:
                    if not num.isnumeric():
                        current_app.logger.error(str(num))
                        return jsonify(err_no=RET.DBERR, err_desc='参数错误')
                    num = float(num)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(err_no=RET.DBERR, err_desc='参数错误')
            # 创建要保存的标签字典
            annotation = dict()
            annotation['bbox'] = bbox
            annotation['category_id'] = category_id
            annotation['category_name'] = category_name
            annotation['segmentation'] = segmentation
            image_site = data.get('image')
            image = Image.query.filter_by(site=str(image_site).split('/', 4)[4]).first()

            label_url_path = current_app.config['NGINX_SITE'] + fun.getInfo(image.label_path)['group_file_id']
            # 读取json文件内容
            file = urllib2.urlopen(label_url_path)
            tmpIm = cStringIO.StringIO(file.read())
            label_date = tmpIm.read()
            label_json_date = json.loads(label_date)

            for label_json_dict in label_json_date['annotation']:
                if label_json_dict['bbox'] == old_bbox:
                    old_label_name = label_dict['category_name']
                    old_label = Label.query.filter_by(collection_id=collection_id,
                                                      old_label_name=old_label_name).first()
                    old_label.count -= 1
                    label_json_date['annotation'].remove(label_json_dict)
                    label_json_date['annotation'].append(annotation)

            label_date = json.dumps(label_json_date)
            # 保存修改后的json文件
            new_label_path = fun.upload(label_date, file_ext_name='json')
            # 删除原json文件
            fun.remove(image.label_path)
            # 修改数据库json文件存储路径
            image.label_path = new_label_path['filename']
            label.count += 1
            db.session.commit()
        else:
            return jsonify(RET.PARAMERR, err_desc='参数缺失')

    return jsonify(err_no=RET.OK, err_desc='修改成功')


@_tag.route('/tagging/delete_label', methods=['POST'])
def delete_label():
    """删除标签"""
    data = request.get_json()
    state = data.get('classification')
    collection_id = data.get('collection_id')
    if state:
        label_id = state['category_id']
        try:
            label = Label.query.filter_by(collection_id=collection_id, label_id=label_id).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(err_no=RET.DBERR, err_desc='查询失败')
        if not label:
            return jsonify(err_no=RET.NODATA, err_desc='没有该标签')

        image_site = data.get('image')
        image = Image.query.filter_by(site=str(image_site).split('/', 4)[4]).first()

        label_url_path = current_app.config['NGINX_SITE'] + fun.getInfo(image.label_path)['group_file_id']
        # 读取json文件内容
        file = urllib2.urlopen(label_url_path)
        tmpIm = cStringIO.StringIO(file.read())
        label_date = tmpIm.read()
        label_json_date = json.loads(label_date)
        old_label_name = label_json_date['classification'][0]['category_name']
        old_label = Label.query.filter_by(collection_id=collection_id, name=old_label_name).first()
        old_label.count -= 1
        del label_json_date['classification'][0]

        label_date = json.dumps(label_json_date)
        # 保存修改后的json文件
        new_label_path = fun.upload(label_date, file_ext_name='json')
        # 删除原json文件
        fun.remove(image.label_path)
        image.label_path = new_label_path['filename']
        db.session.commit()

    # 检测/分割标注
    for label_dict in data.get('annotation'):
        category_id = label_dict['category_id']
        print('label_dict', label_dict)
        old_bbox = label_dict['old_bbox']
        old_bbox = [float(d) for d in old_bbox.split(',')]
        try:
            label = Label.query.filter_by(collection_id=collection_id, label_id=category_id).first()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(err_no=RET.DBERR, err_desc='查询失败')
        if not label:
            return jsonify(err_no=RET.NODATA, err_desc='没有该标签')

        image_site = data.get('image')
        image = Image.query.filter_by(site=str(image_site).split('/', 4)[4]).first()
        label_url_path = current_app.config['NGINX_SITE'] + fun.getInfo(image.label_path)['group_file_id']
        # 读取json文件内容
        file = urllib2.urlopen(label_url_path)
        tmpIm = cStringIO.StringIO(file.read())
        label_date = tmpIm.read()
        label_json_date = json.loads(label_date)

        for label_json_dict in label_json_date['annotation']:
            bbox = [float(d) for d in label_json_dict['bbox']]
            if bbox == old_bbox:
                print('old_bbox = ', old_bbox)
                old_label_id = label_dict['category_id']
                old_label = Label.query.filter_by(collection_id=collection_id, label_id=old_label_id).first()
                old_label.count -= 1
                label_json_date['annotation'].remove(label_json_dict)

        label_date = json.dumps(label_json_date)
        # 保存修改后的json文件
        new_label_path = fun.upload(label_date, file_ext_name='json')
        # 删除原json文件
        fun.remove(image.label_path)
        # 修改数据库json文件存储路径
        image.label_path = new_label_path['filename']
        db.session.commit()

    return jsonify(err_no=RET.OK, err_desc='删除成功')
