# -*- coding:utf-8 -*-
import os

import redis


class Config:
    """基本配置参数"""
    # import os /import base64 / a = os.urandom(20) / base64.b64encode(a)

    SECRET_KEY = "TQ6uZxn+SLqiLgVimX838/VplIsLbEP5jV7vvZ+Ohqw="
    #SQLALCHEMY_DATABASE_URI = "mysql://root:mmlab_16433@127.0.0.1/dataset"
    SQLALCHEMY_DATABASE_URI = "mysql://root:@localhost/DS"  # 已连接本地数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    NGINX_SITE = "http://218.206.177.134:8888/"
    NGINX_LABEL_SITE = "http://218.206.177.134:8888/"
    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = 86400  # session数据的有效期秒
    ADMIN = 'admin'
    ADMIN_EMAIL = 'admin@163.com'

    SQLALCHEMY_ECHO = False


class DevelopmentConfig(Config):
    """开发模式的配置参数"""
    DEBUG = False


class ProductionConfig(Config):
    """生产环境的配置参数"""
    pass


config = {
    "development": DevelopmentConfig,  # 开发模式
    "production": ProductionConfig  # 生产/线上模式
}
