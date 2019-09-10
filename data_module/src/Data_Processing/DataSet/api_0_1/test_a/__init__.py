# -*- coding:utf-8 -*-
from flask import Blueprint
_test_1 = Blueprint('test_1', __name__)
# 把拆分出去的视图导入到创建蓝图对象地方
from . import test_1
