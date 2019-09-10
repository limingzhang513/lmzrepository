# -*- coding:utf-8 -*-
from flask_migrate import Migrate, MigrateCommand   # 依赖flask_script模块，主要做数据库迁移
from flask_script import Manager
import requests

from DataSet import create_app, db

app = create_app('production')
manager = Manager(app)

Migrate(app, db)
manager.add_command('db', MigrateCommand)
"""
新增命令：
python manage.py db init
python manage.py db migrate # 等价于django的makemigrations，本地有
python manage.py db upgrade #  等价于django的migrate  数据库有，数据库迁移
"""

if __name__ == '__main__':
    # print app.url_map
    # print app.name
    manager.run()  # manger 增加了runserver的命令
