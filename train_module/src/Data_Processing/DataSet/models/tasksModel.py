# !/usr/bin/python2
# -*- coding:utf-8 -*-

from DataSet import db
from . import BaseModel


class Tasks(db.Model, BaseModel):

    __tablename__ = 'task_models'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(128))
    state = db.Column(db.String(32), default="训练中")
    train_dataset_id = db.Column(db.Integer, nullable=False)
    train_dataset_var = db.Column(db.String(128), nullable=False)
    train_dataset_path = db.Column(db.String(256))
    test_dataset_id = db.Column(db.Integer, nullable=False)
    test_dataset_var = db.Column(db.String(128), nullable=False)
    test_dataset_path = db.Column(db.String(256))
    parameter = db.Column(db.String(256))
    user_id = db.Column(db.Integer)
    model_id = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        task_dict = {
            "task_id": self.id,
            "task_name": self.name,
            "task_description": self.description,
            "task_state": self.state,
            "task_create_time": self.create_time
        }
        return task_dict

    def to_dict_detail(self):
        task_dict_detail = {
            "task_id": self.id,
            "task_name": self.name,
            "task_description": self.description,
            "task_create_time": self.create_time,
            "task_state": self.state,
            "train_data_id": self.train_dataset_id,
            "parameter": self.parameter,
        }
        return task_dict_detail

    @staticmethod
    def from_json(json_model, frame):
        name = json_model.get('name')
        description = json_model.get('description')
        model_id = json_model.get('model_id')
        train_dataset_id = json_model.get('train_dataset_id')
        train_dataset_var = json_model.get('train_var_ids')
        test_dataset_id = json_model.get('test_dataset_id')
        test_dataset_var = json_model.get('test_var_ids')
        if not all([name, model_id, train_dataset_id, train_dataset_var, test_dataset_id, test_dataset_var]):
            return None
        if not (isinstance(train_dataset_var, list) or isinstance(test_dataset_var, list)):
            return None
        if frame == 1:
            # kears
            if 'batch_size' in json_model and not isinstance(json_model['batch_size'], int):
                return None
            if 'epoch'in json_model and not isinstance(json_model['epoch'], int):
                return None
            if 'mean' in json_model and not isinstance(json_model['mean'], list):
                return None
            if 'scale' in json_model and not (0 < json_model['scale'] < 1):
                return None
            if 'mirror' in json_model and not isinstance(json_model['mirror'], bool):
                return None
            if 'vertical_flip' in json_model and not isinstance(json_model['vertical_filp'], bool):
                return None
            if 'lr_policy' in json_model and not (json_model['lr_policy'] in [0, 1]):
                return None
            if 'optimizer' in json_model and not (json_model['optimizer'] in [0, 1]):
                return None
        if frame == 2:
            #caffe
            if 'batch_size' in json_model and not isinstance(json_model['batch_size'], int):
                return None
            if 'max_iter'in json_model and not isinstance(json_model['max_iter'], int):
                return None
            if 'mean' in json_model and not isinstance(json_model['mean'], list):
                return None
            if 'scale' in json_model and not (0 < json_model['scale'] < 1):
                return None
            if 'mirror' in json_model and not isinstance(json_model['mirror'], bool):
                return None
            if 'base_lr' in json_model and not isinstance(json_model['base_lr'], float):
                return None
            if 'lr_policy' in json_model and not (json_model['lr_policy'] in [0, 1]):
                return None
            if 'gamma' in json_model and not isinstance(json_model['gamma'], float):
                return None
            if 'optimizer' in json_model and not (json_model['optimizer'] in [0, 1]):
                return None
            if 'test_interval' in json_model and not isinstance(json_model['test_interval'], int):
                return None
        return Tasks(name=name, description=description, model_id=model_id, train_dataset_id=train_dataset_id,
                     train_dataset_var=str(train_dataset_var), test_dataset_id=test_dataset_id, test_dataset_var=str(test_dataset_var))

    @staticmethod
    def from_json_caffe(json_model):
        name = json_model.get('name')
        description = json_model.get('description')
        model_id = json_model.get('model_id')
        train_dataset_id = json_model.get('train_dataset_id')
        train_dataset_var = json_model.get('train_dataset_var')
        test_dataset_id = json_model.get('test_dataset_id')
        test_dataset_var = json_model.get('test_dataset_var')
        if not all([name, model_id, train_dataset_id, train_dataset_var, test_dataset_id, test_dataset_var]):
            return None
        if not (isinstance(train_dataset_var, list) or isinstance(test_dataset_var, list)):
            return Nonejson_model.get('parameter')
        return Tasks(name=name, description=description, model_id=model_id, train_dataset_id=train_dataset_id,
                     train_dataset_var=train_dataset_var, test_dataset_id=test_dataset_id,
                     test_dataset_var=test_dataset_var)
