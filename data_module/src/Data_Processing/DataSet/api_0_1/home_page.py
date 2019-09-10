# # -*- coding:utf-8 -*-
#
# from DataSet.token import auth
# import json
# from flask import current_app, jsonify
# from DataSet import redis_store
# from DataSet.models.userModel import User
# from DataSet.utils.serial_code import RET
# from . import api
#
#
# @api.route('/data_module/get_datasets_list', methods=['GET'])
# @login_request
# def get_public():
#     """
#     数据集 公共首页
#     :return:
#     """
#     try:
#         public = redis_store.get('我的收藏（首页）')
#     except Exception as e:
#         current_app.logger.error(e)
#         public = None
#     if public:
#         current_app.logger.info('%s' % g.user_id)
#         return '{"err_no":0,"err_desc":"OK","data":%s}' % public
#
#     try:
#         public = PublicCollection.query.filter_by(user_id=g.user.id).all()
#
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(err_no=RET.DBERR, err_desc='查询数据集信息异常')
#     if not public:
#         return jsonify(errno=RET.NODATA, err_desc='无数据集信息')
#     my_list = []
#     for i in public:
#         my_list.append(i.to_dict())
#     my_json = json.dumps(my_list)
#     try:
#         redis_store.setex('我的收藏（首页）',7200, my_json)
#     except Exception as e:
#         current_app.logger.error(e)
#     resp = '{"err_no":0,"err_desc":"OK","data":%s}' % my_json
#     return resp
#
#
# @api.route('/data_module/get_datasets_list/<int:public_id>', methods=['GET'])
# @login_request
# def get_public_info(public_id):
#     """
#     数据集 公共详情
#     :return:
#     """
#     try:
#         ret = redis_store.get('public_info_%s' % public_id)
#     except Exception as e:
#         current_app.logger.error(e)
#         ret = None
#     if ret:
#         current_app.logger.info('hit redis public detail info')
#         return '{"err_no:0","err_desc:OK","data":%s}' % ret
#     try:
#         public = PublicCollection.query.get(public_id)
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(err_no=RET.DBERR, err_desc='Query collection failed')
#     if not public:
#         return jsonify(err_no=RET.DBERR, err_desc='No such dataset')
#     try:
#         public_data = public.to_full_dict()
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(err_no=RET.DBERR, err_desc='The query fails')
#     public_json = json.dumps(public_data)
#     try:
#         redis_store.setex('public_info_%s' % public_id, 7200, public_json)
#     except Exception as e:
#         current_app.logger.error(e)
#     resp = '{"err_no:0", "err_desc:OK","data":{"user_id:%s","public:%s"}}' % (g.user_id, public_json)
#     return resp
#
#
#
#
#
#
#
