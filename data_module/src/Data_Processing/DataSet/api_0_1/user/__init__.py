# -*- coding:utf-8 -*-
from flask import Blueprint

api = Blueprint('api', __name__)
# , subdomain='api'
# 把拆分出去的视图导入到创建蓝图对象地方
from . import view


