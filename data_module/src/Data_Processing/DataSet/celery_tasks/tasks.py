# -*- coding:utf-8 -*-
import os
import base64
import urllib2
import zipfile
import cStringIO
from manage import app
from DataSet import db
from io import BytesIO
from celery import Celery
from PIL import Image as image_pil
from flask import current_app, json
from DataSet.fastdfs.view import fun
# from DataSet.celery_tasks import AI_label_list
from DataSet.utils.change_json_file import storage, cjf
from DataSet.utils.create_label_file import image_size, clf
from DataSet.models import Collection, Image, Version, Label, User, Share
from DataSet.api_0_1.image_detection_recognition.image_detection_result \
    import image_detection_result_list as AI_label_list


# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/5',
# app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/6'
# celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
# celery.conf.update(app.config)

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/5',
    CELERY_RESULT_BACKEND='redis://localhost:6379/6'
)


def make_celery(app):
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    # TaskBase = ContextTask
    return celery


celery = make_celery(app)


@celery.task()
def classification(status, table_site, upload_image_site, collection, label_name):
    """
    分类/人脸
    :param status: 状态，----lmz改-》标注
    :param table_site: 对应表文件
    :param upload_image_site: 图片文件
    :param collection: 集合id
    :param label_name: 标签集合
    :return:
    """
    with app.app_context():
        collections = Collection.query.filter_by(id=collection).first()
        table_list = []
        error_list = []
        for file_name, up_file in upload_image_site.items():
            up_file = base64.b64decode(up_file)
            images = storage(up_file, collections, file_name)
            size = image_size(up_file)
            if status == 'appoint_table':
                # 对应表
                if table_site is None:
                    return '{"err_no": "1", "err_desc": "参数缺失"}'
                try:
                    if not table_list:
                        for i in table_site.split('\r\n'):
                            table_list.append(i.split(':')[0])
                    tables = table_site.split(file_name + ':')[1]
                    labels = Label.query.filter_by(name=tables.split('\r\n')[0]).first()
                    if file_name in table_list and labels is not None:
                        # 标注上传
                        clf.classification(images, size, labels.label_id, labels.name)
                    else:
                        clf.default(images, size)
                except Exception as e:
                    fun.remove(images.site)
                    current_app.logger.error(e)
                    error_list.append(e)

            elif status == 'default':
                # 未标注
                if not upload_image_site:
                    return '{"err_no": "1", "err_desc": "参数缺失"}'
                try:
                    clf.default(images, size)
                except Exception as e:
                    current_app.logger.error(e)
                    fun.remove(images.site)
                    error_list.append(e)

            elif status.split(':')[1] in label_name:
                # 标注上传
                try:
                    label_data = Label.query.filter_by(collection_id=collection, label_id=status.split(':')[0]).first()
                    if label_data is None:
                        return '{"err_no": "1", "err_desc": "没有此标签"}'
                    if not upload_image_site:
                        return '{"err_no": "1", "err_desc": "参数缺失"}'
                    if status.split(':')[1] != label_data.name:
                        return '{"err_no": "1", "err_desc": "错误的标签ID"}'
                    clf.classification(images, size, status.split(':')[0], status.split(':')[1])
                except Exception as e:
                    fun.remove(images.site)
                    current_app.logger.error(e)
                    error_list.append(e)
                    db.session.delete(images)
                    db.session.commit()

            else:
                fun.remove(images.site)
                db.session.delete(images)
                db.session.commit()

        same_images_clean(collection)

        return '{"err_no": "0", "err_desc": "OK", "上传张数": "%s", "失败张数": "%s", "错误名称": "%s"}' % \
               (len(upload_image_site), len(error_list), error_list)


@celery.task()
def detection(table_site, upload_image_site, label_file, collection):
    """
    检测/分割
    :param table_site: 对应表
    :param upload_image_site: 图片
    :param label_file: 标注文件
    :param collection: 集合id
    :return:
    """
    with app.app_context():
        collection_id = collection
        collection = Collection.query.filter_by(id=collection).first()

        label_file_name = []  # 标注列表名，有后缀
        label_list = []  # 标注列表名，无后缀
        if upload_image_site and label_file:
            for l_file in label_file:
                label_file_name.append(l_file)
                label_list.append(l_file.split('.')[0])

        table_name_list = []  # 对应表,图片名
        table_file_list = []  # 对应表，标注文件名
        error_list = []
        method = 'default'
        for file_name, up_file in upload_image_site.items():
            up_file = base64.b64decode(up_file)
            images = storage(up_file, collection, file_name)
            size = image_size(up_file)

            if all([table_site, upload_image_site, label_file, collection]):
                method = 'ap_table'
                # 对应表
                try:
                    if not all([table_name_list, table_file_list]):
                        for i in table_site.split('\r\n'):
                            table_name_list.append(i.split(':')[0])
                            table_file_list.append(i.split(':')[1])

                    if file_name in table_name_list and \
                            table_site.split(file_name + ':')[1].split('\r\n')[0] in label_file_name:
                        tagging_function(file_name, label_file, images, size, collection)
                    else:
                        clf.default(images, size)
                except Exception as e:
                    fun.remove(images.site)
                    current_app.logger.error(e)
                    error_list.append(e)

            elif all([upload_image_site, label_file, collection]):
                method = 'label'
                # 已经标注上传，未选择对应表
                try:
                    if file_name.split('.')[0] in label_list:
                        tagging_function(file_name, label_file, images, size, collection)
                    else:
                        clf.default(images, size)
                except Exception as e:
                    fun.remove(images.site)
                    current_app.logger.error(e)
                    error_list.append(e)

            elif all([upload_image_site, collection]):
                method = 'no_label'
                # 未标注
                try:
                    clf.default(images, size)
                except Exception as e:
                    fun.remove(images.site)
                    current_app.logger.error(e)
                    error_list.append(e)

            else:
                return '{"err_no": "1", "err_desc": "参数缺失"}'
        same_images_clean(collection_id)

        return '{"err_no": "0", "err_desc": "OK", "上传张数": "%s", "失败张数": "%s", "错误名称": "%s", "method":"%s"}' % \
               (len(upload_image_site), len(error_list), error_list, method)


@celery.task()
def delete_version(status, version_id):
    """
    版本删除
    :param status: 状态
    :param version_id: 版本id
    :return:
    """
    from DataSet.rabbitMQ.task_queue_client import delete_version_task
    # 查出版本下原有图片json路径  减掉对应label次数， 删除该版本的压缩包
    with app.app_context():
        # 以下是队列内容
        versions = Version.query.filter_by(id=version_id).one()
        if versions.zip_path:
            fun.remove(versions.zip_path)
        label_dict = {}
        number = 0
        for image in versions.images:
            label_url_path = current_app.config['NGINX_SITE'] + fun.getInfo(image.label_path)['group_file_id']
            label_url_path = delete_version_task(label_url_path)
            files = urllib2.urlopen(label_url_path)
            tmpIm = cStringIO.StringIO(files.read())
            label_data = tmpIm.read()
            label_json_data = json.loads(label_data)

            if 1 == versions.collection.type:
                json_label_id = label_json_data['classification'][0]['category_id']
                if json_label_id in label_dict:
                    label_dict[json_label_id] += 1
                else:
                    label_dict[json_label_id] = 1

            elif 2 == versions.collection.type:
                number += len(label_json_data['annotation'])

                for i in label_json_data['annotation']:
                    json_label_id = i['category_id']
                    if json_label_id in label_dict:
                        label_dict[json_label_id] += 1
                    else:
                        label_dict[json_label_id] = 1
        for label_id, label_count in label_dict.items():
            # 标签中每个标签的使用量
            old_count = db.session.query(Label.count).filter(Label.label_id == label_id,
                                                             Label.collection_id == versions.collection.id).scalar()
            # 当前标签
            label = Label.query.filter_by(label_id=label_id, collection_id=versions.collection.id).first()
            # 更新当前标签使用量为  新+旧
            if (old_count - label_count) < 0:
                label.count = 0
            else:
                label.count = old_count - label_count
                # 将标签id 名字使用量存入字典
            db.session.commit()

            # 以上是队列内容

            if status == 'delete':
                for image in versions.images:
                    image.version_id = None
                    db.session.add(image)
                    db.session.commit()
                db.session.delete(versions)
                db.session.commit()
            elif status == 'delete_all':
                for image in versions.images:
                    if image.site:
                        fun.remove(image.site.encode())
                    if image.label_path:
                        fun.remove(image.label_path.encode())
                    db.session.delete(image)
                    db.session.commit()
                db.session.delete(versions)
                db.session.commit()
            else:
                current_app.logger.info('错误参数{}'.format(status))
                return '{"err_no": "2", "err_desc": "参数有误"}'
            return '{"err_no": "0", "err_desc": "OK"}'


@celery.task()
def create_version(collection_id, name, image_count, old_version):
    """
    版本创建归并
    :param collection_id: 数据集id
    :param name: 版本名称
    :param image_count: 上传图片数量
    :param old_version: 要合并的版本名称
    :return:
    """
    from DataSet.rabbitMQ.task_queue_client import create_version_task
    with app.app_context():
        collection = Collection.query.filter_by(id=collection_id).first()
        now_version = Version.query.filter_by(collection_id=collection_id, name=name).first()
        now_version_list = list()
        now_version_list.append(now_version.id)
        now_version_list.append(now_version.name)

        if image_count:
            no_version_images = Image.query.filter(
                Image.collection_id == collection_id, Image.status == 3, Image.version_id.is_(None)).limit(
                image_count)
            for n_version_images in no_version_images:
                n_version_images.version_id = now_version.id
                db.session.add(n_version_images)
                db.session.commit()
        if old_version:
            versions_list_name = [c_version.name for c_version in collection.versions]
            for i in old_version:
                if i not in versions_list_name:
                    return '{"err_no": "1", "err_desc": "找不到该版本"}'
            try:
                for old_name in old_version:
                    versions = Version.query.filter_by(collection_id=collection_id, name=old_name).first()  # 原版本
                    for image in versions.images:  # 查出原版本下所有图片
                        image.version_id = now_version.id
                        db.session.add(image)
                        db.session.commit()
                    db.session.delete(versions)
                    db.session.commit()
            except Exception as e:
                current_app.logger.error(e)
                return '{"err_no": "2", "err_desc": "参数有误", "date": %s}' % e
        # 以下是队列内容
        collection = Collection.query.filter_by(id=collection_id).first()
        versions = Version.query.filter_by(collection_id=collection_id, name=name).first()
        label_dict = {}
        number = 0
        width = 0
        height = 0
        label_info = {}
        path_name = create_version_task(now_version_list)
        newZip = zipfile.ZipFile(path_name, 'w')
        for image in versions.images:
            label_url_path = current_app.config['NGINX_SITE'] + fun.getInfo(image.label_path)['group_file_id']
            files = urllib2.urlopen(label_url_path)
            tmpIm = cStringIO.StringIO(files.read())
            label_data = tmpIm.read()
            # print label_data
            label_json_data = json.loads(label_data)
            image_label_path = fun.download(image.label_path)
            image_site = fun.download(image.site)
            newZip.writestr(image.label_path[10:], image_label_path, compress_type=zipfile.ZIP_DEFLATED)
            newZip.writestr(image.site[10:], image_site, compress_type=zipfile.ZIP_DEFLATED)
            if 1 == collection.type:
                json_label_id = label_json_data['classification'][0]['category_id']
                if json_label_id in label_dict:
                    label_dict[json_label_id] += 1
                else:
                    label_dict[json_label_id] = 1
            elif 2 == collection.type:
                number += len(label_json_data['annotation'])
                for i in label_json_data['annotation']:
                    json_label_id = i['category_id']
                    if json_label_id in label_dict:
                        label_dict[json_label_id] += 1
                    else:
                        label_dict[json_label_id] = 1
                    width += i['bbox'][2]
                    height += i['bbox'][3]
        newZip.close()
        new_zip = fun.uploads(path_name)
        now_version.zip_path = new_zip.get('file_id')
        os.remove(path_name)
        if 2 == collection.type:
            versions.average_number = number / len(versions.images)
            versions.mean_size = "{:.1f}*{:.1f}".format(width / number, height / number)
            db.session.commit()
        # 原数据如何与新数据结合
        for label_id, label_count in label_dict.items():
            # 标签中每个标签的使用量
            old_count = db.session.query(Label.count).filter(Label.label_id == label_id,
                                                             Label.collection_id == collection_id).scalar()
            # 当前标签
            label = Label.query.filter_by(label_id=label_id, collection_id=collection_id).first()
            # 更新当前标签使用量为  新+旧
            label.count = old_count + label_count
            # 将标签id 名字使用量存入字典
            label_info[label_id] = [label.name, label_count]
            db.session.commit()
        # 将标签信息存入版本描述
        now_version.label_info = json.dumps(label_info)
        db.session.commit()
        # 以上是队列内容
        return '{"err_no": "0", "err_desc": "OK"}'


@celery.task()
def delete_set(uid, name):
    """
    数据集删除
    :param uid: 用户id
    :param name: 数据集名称
    :return:
    """
    from DataSet.rabbitMQ.task_queue_client import delete_set_task
    with app.app_context():
        try:
            collection = Collection.query.filter_by(user_id=uid, name=name).first()
            if collection.images:
                for i in collection.images:
                    if i.site:
                        fun.remove(i.site)
                    if i.label_path:
                        fun.remove(i.label_path)
                    db.session.delete(i)
                    db.session.commit()
            if collection.labels:
                for i in collection.labels:
                    db.session.delete(i)
                    db.session.commit()
            if collection.versions:
                for i in collection.versions:
                    db.session.delete(i)
                    db.session.commit()
            # 以下
            user = User.query.filter_by(id=uid).first()
            share_users = user.share
            my_share = share_users.my_share  # 我的分享 str
            if my_share:
                #  队列开启
                task_my_share = delete_set_task(my_share)
                dict_my_share = eval(task_my_share)
                data_dict = {}
                for key, value in dict_my_share.items():
                    for i in value:
                        if i == collection.id:
                            value.remove(i)
                            data_dict[key] = value
                            if not value:
                                del dict_my_share[key]
                Share.query.filter_by(id=uid).update({'my_share': json.dumps(data_dict) if dict_my_share else None})
                db.session.commit()
                for data_id, data_info in data_dict.items():
                    Share.query.filter_by(id=data_id).update(
                        {'share_collection': json.dumps(data_info) if data_info else None})
                    db.session.commit()
            db.session.delete(collection)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return '{"err_no": "2", "err_desc": "信息保存异常", "data": %s}' % e

        return '{"err_no": "0", "err_desc": "OK"}'


@celery.task()
def spider(
        spider_dict):  # spider_dict 是后端从前端post表单获取到用户给的参数形式为{'keyword':xx, 'spider_page_num':xx, 'start_page':xx， 'number'：xx}
    """爬虫任务"""
    from DataSet.rabbitMQ.task_queue_client import spider_task
    with app.app_context():
        site_list = list()
        print spider_dict
        spider_image_list = spider_task(spider_dict)
        spider_image_list = json.loads(spider_image_list)
        print spider_image_list
        for spider_image in spider_image_list:
            file = urllib2.urlopen(spider_image)
            tmpIm = cStringIO.StringIO(file.read())
            # c = tmpIm.read()s
            site = fun.upload(tmpIm.read(), file_ext_name='jpg')
            site_list.append(site)

            # 数据库存储
            for spider_file in site_list:
                image = Image()
                image.name = spider_file.get('filename')
                image.site = spider_file.get('file_id')
                spider_dict1 = json.loads(spider_dict)
                print(spider_dict1['collection_id'])
                image.collection_id = spider_dict1['collection_id']
                print image.collection_id
                db.session.add(image)
                db.session.commit()
                images = Image.query.filter_by(name=image.name).first()

                image_url_path = current_app.config['NGINX_SITE'] + fun.getInfo(images.site)['group_file_id']

                file = urllib2.urlopen(image_url_path)
                size = image_size(file.read())

                clf.default(images, size)

            collection_id = spider_dict1['collection_id']

            same_images_clean(collection_id)

        return site_list


@celery.task()
def same_images_clean(collection_id):
    """图片去重处理"""
    from DataSet.rabbitMQ.task_queue_client import same_images_clean_task
    with app.app_context():

        images_path_list = list()
        images = None

        try:
            images = Image.query.filter(Image.collection_id == collection_id, Image.status < 2).all()
        except Exception as e:
            current_app.logger.error(e)

        if not images:
            return 'no images'

        for image in images:
            # print(image)
            # print(fun.getInfo(image.site))
            image_site = current_app.config['NGINX_SITE'] + fun.getInfo(image.site)['group_file_id']
            images_path_list.append(image_site)
        # 队列开启
        response_image_list = same_images_clean_task(images_path_list)

        # 解析队列返回的josn数据
        response_image_list = json.loads(response_image_list)
        delete_imglist = response_image_list[1]
        imgList = response_image_list[0]

        # 删除数据库重复图片
        if delete_imglist:
            for i in delete_imglist:
                i = str(i).split('/', 4)[4]
                delete_image = Image.query.filter_by(site=i).first()
                fun.remove(delete_image.label_path)  # 删除本地存储的标签文件
                try:
                    db.session.delete(delete_image)
                    db.session.commit()
                except Exception as e:
                    current_app.logger.error(e)
                    db.session.rollback()
                fun.remove(i)  # 删除本地存储的图片

        # 修改去重后的图片状态为待标注
        ch_img = list(set(imgList).difference(set(delete_imglist)))

        for i in ch_img:
            i = str(i).split('/', 4)[4]
            change_state = Image.query.filter_by(site=i).first()
            try:
                change_state.status = 1  # 代表待标注状态的数字
                db.session.commit()
            except Exception as e:
                current_app.logger.error(e)
                db.session.rollback()


# @celery.task()
# def preprocessing(collection_id, model, label_name, c_label_name_list):
def preprocessing(collection_id, label_info):
    """预标注任务"""
    from DataSet.rabbitMQ.task_queue_client import preprocessing_task
    with app.app_context():  # 开辟一个上下文管理空间

        # get config
        model = -1
        pre_model = list()
        label_name_list = list()
        c_label_name_list = list()
        for key in label_info:
            model = int(key.split('_')[0])
            pre_model.append(int(key.split('_')[1]))
            for k in label_info[key]:
                label_name_list.append(label_info[key][k])
                c_label_name_list.append(k)

        images = None
        try:
            images = Image.query.filter_by(collection_id=collection_id, status=1).all()
        except Exception as e:
            current_app.logger.error(e)
        if not images:
            print(label_info, 'no images')

        for image in images:
            # get image url
            image_obj = Image.query.filter_by(id=image.id).first()
            image_url_path = current_app.config['NGINX_SITE'] + fun.getInfo(image_obj.site)['group_file_id']
            file = urllib2.urlopen(image_url_path)  # 获取图片

            # get image file
            tmpIm = cStringIO.StringIO(file.read())  # Return a StringIO-like stream for reading or writing
            img = image_pil.open(tmpIm)  # PIL模块处理图像
            if img.mode in ('RGBA', 'LA', 'P'):
                background = image_pil.new('RGB', img.size)
                background.paste(img)
                img = background

            # base64
            bs = BytesIO()
            img.save(bs, format="JPEG")
            b64 = base64.b64encode(bs.getvalue())

            # get request
            type_b64_list = list()
            type_b64_list.append(b64)
            type_b64_list.append(model)
            type_b64_list.append(pre_model)

            # request
            json_data = preprocessing_task(type_b64_list)  # 指定预处理队列处理
            json_data = json.loads(json_data)

            # print( 'label results ', json_data )

            # get label
            label_url_path = current_app.config['NGINX_SITE'] + fun.getInfo(image_obj.label_path)['group_file_id']
            # 读取json文件内容
            file = urllib2.urlopen(label_url_path)
            tmpIm = cStringIO.StringIO(file.read())
            label_data = tmpIm.read()
            label_json_data = json.loads(label_data)

            # print( 'old label_json_data ', label_json_data )

            isSuccess = False
            # 模型1
            if model == 1:
                labels = list()
                for key in json_data:
                    labels = labels + json_data[key]['labels']

                for label_dict in labels:
                    if label_dict['content'] in c_label_name_list:
                        label_name = label_name_list[c_label_name_list.index(label_dict['content'])]
                        label = Label.query.filter_by(collection_id=collection_id, name=label_name).first()
                        # 创建要保存的标签字典
                        classification = dict()
                        classification['category_id'] = label.label_id
                        classification['category_name'] = label_name

                        label_json_data['classification'] = classification
                        label.count += 1
                        isSuccess = True
                    else:
                        print('other label: ', label_dict['content'])

            # 模型2
            elif model == 2:
                detection = list()
                for key in json_data:
                    detection = detection + json_data[key]['detection']

                for label_dict in detection:
                    pmid = label_dict['pre_model']
                    if float(label_dict['score']) > 0.3:
                        AI_label_name = AI_label_list[pmid][label_dict['label_id']].decode('utf-8')
                        # print( 'c_label_name_list', AI_label_name, c_label_name_list )
                        if AI_label_name in c_label_name_list:
                            label_name = label_name_list[c_label_name_list.index(AI_label_name)]
                            label = Label.query.filter_by(collection_id=collection_id, name=label_name).first()
                            # 标注框坐标转换
                            bbox_list = list()
                            bbox_list.append('%.2f' % (float(label_dict['xmin'])))
                            bbox_list.append('%.2f' % (float(label_dict['ymin'])))
                            bbox_list.append('%.2f' % (float(label_dict['xmax']) - float(label_dict['xmin'])))
                            bbox_list.append('%.2f' % (float(label_dict['ymax']) - float(label_dict['ymin'])))
                            # 创建json annotation字典
                            annotation = dict()
                            annotation['bbox'] = bbox_list
                            annotation['category_id'] = label.label_id
                            annotation['category_name'] = label.name
                            annotation['segmentation'] = []
                            if 'feaData' in label_dict:
                                annotation['feaData'] = label_dict['feaData']

                            label_json_data['annotation'].append(annotation)
                            label.count += 1
                            isSuccess = True

            if isSuccess:
                # print( 'label_json_data', label_json_data )
                label_data = json.dumps(label_json_data)
                # 保存修改后的json文件
                new_label_path = fun.upload(label_data, file_ext_name='json')
                # 删除原json文件
                fun.remove(image.label_path)
                # 修改数据库json文件存储路径
                image_obj.label_path = new_label_path['filename']
                # 修改图片状态
                image_obj.status = 2
                db.session.commit()
            else:
                image_obj.status = 2
                db.session.commit()


def tagging_function(file_name, label_file, images, size, collection):
    for l_name, l_file in label_file.items():
        if file_name.split('.')[0] + '.' + l_name.split('.')[1] == l_name:
            if l_name.split('.')[1] == 'xml':
                l_file = base64.b64decode(l_file)
                clf.segmentation(images, size, l_file, collection)

            elif l_name.split('.')[1] == 'json':
                l_file = base64.b64decode(l_file)
                cjf.segmentation(images, size, l_file)
            else:
                clf.default(images, size)
        else:
            continue
