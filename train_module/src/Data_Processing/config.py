# -*- coding:utf-8 -*-

import os
import redis

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """基本配置参数"""

    SECRET_KEY = "TQ6uZxn+SLqiLgVimX838/VplIsLbEP5jV7vvZ+Ohqw="
    SQLALCHEMY_DATABASE_URI = "mysql://root:mmlab_16433@localhost/ds"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = 86400  # session数据的有效期秒
    ADMIN = 'ADMIN'
    CONNECT_TIMEOUT = 5

    # train model pagination
    MODELS_TASKS_PER_PAGE = 5

    # model upload config
    BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
    ALLOWED_EXTENSIONS = set(['h5', 'prototxt', 'caffemodel', 'json'])

    # celery
    CELERY_BROKER_URL = 'redis://localhost:6379/3'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/3'

    # login and get token
    GET_TOKEN_URL = 'http://218.206.177.134:5000/login'

    # token identify
    TOKEN_IDENTIFY_URL = 'http://218.206.177.134:5000/user'

    # get datasets and versions
    GET_DATASET_URL = 'http://218.206.177.134:5000/data_module/list_dataset'
    GET_VERSION_URL = 'http://218.206.177.134:5000/data_module/{}/versions_all'

    # download dataset url
    DOWNLOAD_DS_URL = 'http://192.168.1.137:5000/data_module/download_images'
    # DOWNLOAD_DS_URL = 'http://127.0.0.1:5004/get_file'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    pass


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}
