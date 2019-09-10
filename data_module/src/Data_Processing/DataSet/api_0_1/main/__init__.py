# -*- coding:utf-8 -*-

from flask import Blueprint, make_response

_main = Blueprint('main', __name__)
# 把拆分出去的视图导入到创建蓝图对象地方
from . import collection_view, version_view, share_view