# !/usr/bin/python2
'''
    celery worker register
'''

from DataSet import create_app, celery

app = create_app('development')
app.app_context().push()
