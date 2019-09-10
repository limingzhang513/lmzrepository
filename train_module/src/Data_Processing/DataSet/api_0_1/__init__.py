# !/usr/bin/python2
# -*- coding:utf-8 -*-

from flask import Blueprint
api = Blueprint('api', __name__)
from .user import view
from .models_training import view
from .tasks_training import view


def after_requrst(response):
    if response.headers.get('Content-Type').startswith('text'):
        response.headers['Context-Type'] = 'application/json'
    return response
