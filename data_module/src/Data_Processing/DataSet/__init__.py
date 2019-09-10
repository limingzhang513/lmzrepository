# -*- coding:utf-8 -*-

import redis
import logging
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from config import Config, config
# from flask_wtf import CSRFProtect
from utils.commons import RegexConverter
from logging.handlers import TimedRotatingFileHandler

db = SQLAlchemy()
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# csrf = CSRFProtect()

# 设置日志的记录等级
logging.basicConfig(level=logging.INFO)  # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
# file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
file_log_handler = TimedRotatingFileHandler(filename="logs/log", when="MIDNIGHT", interval=1, backupCount=30)
# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
# formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
formatter = logging.Formatter('{"time": "%(asctime)s", "name": "%(filename)s[line:%(lineno)d]",'
                              ' "levelname": "%(levelname)s", "message": "%(message)s"'
                              '}', "%Y-%m-%d %H:%M:%S")

# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（应用程序实例app使用的）添加日后记录器
logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])  # 导入配置文件
    app.url_map.converters['regex'] = RegexConverter  # 支持路由正则匹配
    db.init_app(app)  # 连接数据库读配置文件
    # csrf.init_app(app)
    Session(app)  # 设置session存储位置，项目设置为redis

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        if request.method == 'OPTIONS':
            response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
            headers = request.headers.get('Access-Control-Request-Headers')
            if headers:
                response.headers['Access-Control-Allow-Headers'] = headers

        if response.headers.get('Content-Type').startswith('text'):
            response.headers['Context-Type'] = 'application/json'

        return response

    from .api_0_1.user import api
    from .api_0_1.admin import _admin
    from .api_0_1.main import _main
    from .api_0_1.spider import _spi
    from .api_0_1.tagging import _tag
    from .api_0_1.image_detection_recognition import _img
    app.register_blueprint(api)
    app.register_blueprint(_main)
    app.register_blueprint(_admin)
    app.register_blueprint(_spi)
    app.register_blueprint(_tag)
    app.register_blueprint(_img)

    return app
