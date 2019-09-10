# !/usr/bin/python2
# -*- coding:utf-8 -*-

import os
import shutil
from datetime import datetime
from DataSet import db
from . import BaseModel


class TrainResult(db.Model, BaseModel):

    __tablename__ = 'result_models'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    model_id = db.Column(db.Integer, nullable=False)
    task_id = db.Column(db.Integer, nullable=False)
    plt_path = db.Column(db.String(512))
    log_path = db.Column(db.String(512))
    trained_path = db.Column(db.String(512))

    @staticmethod
    def check_expire():
        all_result = TrainResult.query.order_by(TrainResult.create_time).all()
        if all_result is None:
            return None
        for obj in all_result:
            if obj.create_time is None:
                continue
            if (datetime.now() - obj.create_time).days >= 30:
                res = TrainResult().del_result(obj)
                if res:
                    db.session.delete(obj)
                    db.session.commit()
        print 'delete all expire trained file and server.log file'

    @staticmethod
    def del_result(obj):
        try:
            if obj.trained_path:
                if os.path.exists(obj.trained_path):
                    shutil.rmtree(obj.trained_path)
            if obj.log_path:
                if os.path.exists(obj.log_path):
                    os.remove(obj.log_path)
        except Exception as e:
            print e
            return None
        return True

    @staticmethod
    def update_log(trained_path, log_path):
        update_obj = TrainResult.query.filter_by(trained_path=trained_path).first()
        if update_obj is None:
            return None
        try:
            update_obj.log_path = log_path
            db.session.add(update_obj)
            db.session.commit()
        except Exception as e:
            print e
            return None
        return 'complete'

