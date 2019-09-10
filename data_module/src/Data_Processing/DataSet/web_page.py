# -*- coding:utf-8 -*-

from flask import Blueprint, current_app, make_response
from flask_wtf import csrf


html = Blueprint("html", __name__)


@html.route("/<regex('.*'):file_name>")
def html_file(file_name):

    if not file_name:
        file_name = "login.html"

    if file_name != "xxxxxxxxxxxxxxxxxxxxxxxxx":  # log
        file_name = "html/" + file_name

    csrf_token = csrf.generate_csrf()
    response = make_response(current_app.send_static_file(file_name))
    # 往客户端浏览器的cookie中写入csrf_token
    response.set_cookie("csrf_token", csrf_token)

    return response