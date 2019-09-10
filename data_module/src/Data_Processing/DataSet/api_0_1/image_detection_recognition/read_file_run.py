# -*- coding:utf-8 -*-
import requests
import time

while True:
    url = 'http://218.206.177.134:5000/file_read/1'

    response = requests.get(url)
    print('labeling finished')
    time.sleep(600)
