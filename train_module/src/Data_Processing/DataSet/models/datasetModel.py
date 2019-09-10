# !/usr/bin/python2
# -*- coding:utf-8 -*-

import os
import json
from datetime import datetime
from DataSet import db
from . import BaseModel


class Dataset(db.Model, BaseModel):

    __tablename__ = 'dataset_models'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    dataset_id = db.Column(db.Integer, nullable=False)
    dataset_var = db.Column(db.String(128), nullable=False)
    dataset_path = db.Column(db.String(512), nullable=False)

    @staticmethod
    def check_expire():
        all_dataset = Dataset.query.order_by(Dataset.create_time).all()
        if all_dataset is None:
            return None
        for obj in all_dataset:
            if obj.create_time is None:
                continue
            if (datetime.now() - obj.create_time).days >= 30:
                res = Dataset().del_dataset(obj)
                if res:
                    db.session.delete(obj)
                    db.session.commit()
        print 'delete all expire dataset'

    @staticmethod
    def del_dataset(obj):
        if obj.dataset_path is None:
            return None
        try:
            ds_objs = json.loads(obj.dataset_path)
            for _, v in ds_objs.items():
                if os.path.exists(v):
                    try:
                        os.remove(v)
                    except Exception as e:
                        print e
                        continue
        except Exception as e:
            print e
            return None
        return True

    @staticmethod
    def create_test_data():
        for i in range(5):
            ds = Dataset(user_id=1, dataset_id=1, dataset_var='[1,2,%s]' % i, dataset_path='/path/test/%s' % i)
            db.session.add(ds)
            db.session.commit()
