# -*- coding:utf-8 -*-
import urllib2
from DataSet.api_0_1.spider import _spi
from DataSet.models import Collection, Image
from flask import jsonify, current_app, request, json
from DataSet.utils.serial_code import RET
from DataSet import db
from DataSet.utils.create_label_file import image_size, clf
from DataSet.fastdfs.view import fun


@_spi.route("/data_module/spider_upload_image", methods=['POST'])
def upload_image():
    """
    爬虫配置
    """
    # 配置参数字典
    from DataSet.celery_tasks.tasks import spider, same_images_clean
    data = request.get_json()
    print(data)
    if not data:
        return jsonify(err_no=RET.PARAMERR, err_desc= '参数缺失')
    collection_id = data['collection_id']
    spider_dict = dict()
    spider_save_list = list()
    try:
        collection = Collection.query.filter_by(id=collection_id).first
        if collection is None:
            return jsonify(err_no=RET.PARAMERR, err_desc='没有该数据集')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(err_no=RET.PARAMERR, err_desc='参数有误')

    data = request.get_json()
    number = data.get('number')
    number = int(number)
    spider_page_num = number/60 + 1
    if not number:
        return jsonify(err_no=RET.PARAMERR, err_desc='参数缺失')

    keywords = data.get('keywords')
    # 关键字搜图
    if keywords:
        keywords = keywords.split(';')
        for keyword in keywords:
            spider_dict['keyword'] = keyword
            spider_dict['spider_page_num'] = spider_page_num
            spider_dict['start_page'] = 1
            spider_dict['number'] = number
            spider_dict['collection_id'] = collection_id
            spider_save_list = spider.delay(json.dumps(spider_dict))

        spider_save_list =  spider_save_list.get()
        print(spider_save_list)

        # 数据库存储
        for spider_file in spider_save_list:
            image = Image()
            image.name = spider_file.get('filename')
            image.site = spider_file.get('file_id')
            image.collection_id = collection_id
            db.session.add(image)
            db.session.commit()
            images = Image.query.filter_by(name=image.name).first()

            image_url_path = current_app.config['NGINX_SITE'] + fun.getInfo(images.site)['group_file_id']

            file = urllib2.urlopen(image_url_path)
            size = image_size(file.read())

            clf.default(images, size)

        collection_id = int(collection_id)

        same_images_clean.delay(collection_id)

    # 以图搜图
    else:
        image = data.get('image')
        print(image)
        if not image:
            return jsonify(err_no=RET.PARAMERR, err_desc='参数缺失')

    return jsonify(err_no=RET.OK, err_desc='爬取结束')
