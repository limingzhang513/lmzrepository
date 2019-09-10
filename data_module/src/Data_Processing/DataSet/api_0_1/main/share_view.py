# # -*- coding:utf-8 -*-
# from flask import current_app, jsonify, g, json, request
# from DataSet import redis_store
# from DataSet.api_0_1.main import _main
# from DataSet.models import Collection, User, Label
# from DataSet.token import auth
# from DataSet.utils.auth_decorator import user_required
# import time
# from DataSet.utils.serial_code import RET
#
#
# @_main.route('/data_module/list_dataset/share', methods=['GET'])
# @auth.login_required
# def share_dataset():
#     """
#     共享数据集--列表
#     :return:
#     """
#     local_time = time.time()
#     try:
#         user = User.query.filter_by(id=g.user.id).first()
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(err_no=RET.DBERR, err_desc='查询数据库错误')
#     try:
#         collection = redis_store.get('share_collection_%s' % user.id)
#     except Exception as e:
#         current_app.logger.error(e)
#         collection = None
#     if collection:
#         current_app.logger.info('%s' % g.user.id)
#         return '{"err_no":"0","err_desc":"OK","data":%s}' % collection
#
#     try:
#         collection= user.share.share_collection
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify(err_no=RET.DBERR, err_desc='查询数据集信息异常')
#     if not collection:
#         return jsonify(err_no=RET.DATAERR, err_desc='没有用户向您共享数据集')
#     my_list = []
#     for i in eval(collection):
#         collections = Collection.query.filter_by(id=i).first()
#         if not collections:
#             continue
#         my_list.append(collections.to_dict())
#     my_json = json.dumps(my_list)
#     try:
#         redis_store.setex('share_collection_%s' % user.id, 7200, my_json)
#     except Exception as e:
#         current_app.logger.error(e)
#
#     try:
#         request_id = request.cookies.get('session')[:36]
#     except EOFError:
#         request_id = {}
#     time_used = int((time.time() * 1000) - int(local_time * 1000))
#
#     resp = '{"err_no": "0", "err_desc": "OK", "time_used": %s, "request_id":"%s", "data": %s}' % \
#            (time_used, request_id, my_json)
#     return resp
#
# # # 共享数据集--详情
# # @_main.route('/data_module/<int:collection_id>/share', methods=['GET'])
# # @auth.login_required
# # def share_dataset_info(collection_id):
# #     """
# #       数据集--详情
# #     共享数据集--详情
# #     :return:
# #     """
# #
# #     local_time = time.time()
# #
# #     try:
# #         user = User.query.filter_by(id=g.user.id).first()
# #     except Exception as e:
# #         current_app.logger.error(e)
# #         return jsonify(errno=RET.DBERR, err_desc='查询数据库错误')
# #     collection = Collection.query.filter_by(user_id=g.user.id, id=collection_id).first()
# #
# #     collections = user.share.share_collection
# #     if not collections:
# #         collections='[]'
# #     if collection_id not in eval(collections) and not collection:
# #         return jsonify(errno=RET.DBERR, err_desc='不存在的数据集')
# #
# #     try:
# #         ret = redis_store.get('data_info_%s' % collection_id)
# #     except Exception as e:
# #         current_app.logger.error(e)
# #         ret = None
# #     if ret:
# #         current_app.logger.info('hit redis personage detail info')
# #         return '{"err_no":"0","err_desc":"OK","data":%s}' % ret
# #
# #     collection = Collection.query.filter_by(id=collection_id).first()
# #
# #     try:
# #         collection_data = collection.to_dict()
# #     except Exception as e:
# #         current_app.logger.error(e)
# #         return jsonify(err_no=RET.DBERR, err_desc='The query fails')
# #
# #     collection_data['images'] = len(collection.images)
# #     versions = {}
# #     if collection.versions:
# #         for i in collection.versions:
# #             versions[i.name] = len(i.images)
# #         collection_data['versions'] = versions
# #
# #     label = Label.query.filter_by(collection_id=collection_id).all()
# #     labels = {}
# #     if label:
# #         collection_data['label_num'] = len(label)
# #         for i in label:
# #             labels[int(i.label_id)]=i.name
# #         collection_data['labels'] = labels
# #     collection_json = json.dumps(collection_data)
# #     try:
# #         redis_store.setex('data_info_%s' % collection_id, 7200, collection_json)
# #     except Exception as e:
# #         current_app.logger.error(e)
# #
# #     request_id = (request.cookies.get('session'))[:36]
# #     time_used = int((time.time() * 1000) - int(local_time * 1000))
# #     resp = '{"err_no":"0", "err_desc":"OK", "time_used": %s, "request_id":"%s", "data": %s}' % \
# #            (time_used, request_id, collection_json)
# #     return resp
#
#
