# -*- coding:utf-8 -*-
from flask import Blueprint
_tag = Blueprint('tag', __name__)
# 把拆分出去的视图导入到创建蓝图对象地方
from . import view