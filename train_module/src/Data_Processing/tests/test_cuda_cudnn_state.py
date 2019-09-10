# !/usr/bin/python3
'''
a script which be used test gpu and cudnn state
'''

from tensorflow.python.client import device_lib
print(device_lib.list_local_devices())
