# !/usr/bin/python2
# -*- coding:utf-8 -*-

import redis
import logging
from celery import Celery
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from config import Config, config
from flask_wtf import CSRFProtect
from DataSet.utils.commons import RegexConverter
from logging.handlers import RotatingFileHandler


db = SQLAlchemy()
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
csrf = CSRFProtect()

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

# 设置日志的记录等级
logging.basicConfig(level=logging.INFO)  # info级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("/home/duduo/workspace/Data_Processing/logs/server.log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(l'
                              'ineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（应用程序实例app使用的）添加日后记录器
logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.url_map.converters['regex'] = RegexConverter
    db.init_app(app)
    Session(app)
    celery.conf.update(app.config)
    from .api_0_1 import api
    app.register_blueprint(api)
    return app
