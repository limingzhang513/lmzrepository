# !/usr/bin/python2
# coding=utf-8
'''
test dataset download server
'''

from flask import Flask, request, jsonify, send_from_directory, abort
from flask_httpauth import HTTPBasicAuth
import os

auth = HTTPBasicAuth()

app = Flask(__name__)


@app.route('/get_file', methods=['get'])
def get_file():
    """
    test download server
    :return:
    """
    filename = './a_test_dataset_file.zip'
    if filename:
        print request.args.get('collection_id')
        print request.args.get('version_id')
        if os.path.isfile(filename):
            return send_from_directory('.', filename, as_attachment=True)
        else:
            return jsonify({"msg": "文件不存在!"})
    else:
        return jsonify({'msg': '文件名不能为空'})


if __name__ == '__main__':
    app.run(port=5004)
