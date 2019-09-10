# -*- coding:utf-8 -*-
import os
import requests as s

url = "http://192.168.112.131:5000/api/users/1"

#假设待上传文件与脚本在同一目录下
dir_path = os.path.abspath(os.path.dirname(__file__))
#待上传文件的路径，这里假设文件名为test.txt
file_path = os.path.join(dir_path, 'xy.prototxt')
print file_path

'''
    field_1,field_2...field_n代表普通字段名
    value_1,value_2...value_n代表普通字段值
    files为文件类型字段

    实际应用中字段名field_n均需要替换为接口抓包得到的实际字段名
    对应的字段值value_n也需要替换为接口抓包得到的实际字段值
'''
files={
    'name': (None, 'hello5'),
    'data_type': (None, '4'),
    'desc': (None, 'test_a'),
    'upload_file': ('xy.prototxt', open('/home/python/Desktop/test_a/xy.prototxt'), 'text/plain')

}

r = s.post(url, files=files)