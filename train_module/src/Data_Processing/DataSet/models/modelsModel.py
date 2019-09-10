# !/usr/bin/python2
# -*- coding:utf-8 -*-

from DataSet import db
from . import BaseModel


class ModelsFrame:
    keras = 1
    caffe = 2


class ModelsType:
    classification = 1
    testing = 2
    division = 3
    face_recognition = 4


class Models(db.Model, BaseModel):

    __tablename__ = 'train_models'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(128))
    frame = db.Column(db.Integer, default=1, nullable=False)
    type = db.Column(db.Integer, default=1, nullable=False)
    define_path = db.Column(db.String(256), nullable=False)
    weight_path = db.Column(db.String(256), nullable=False)
    label = db.Column(db.Integer, nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer)
    version = db.Column(db.String(64), default='None')

    def to_dict(self):
        model_dict = {
            "model_id": self.id,
            "model_name": self.name,
            "model_description": self.description,
            "model_frame": self.frame,
            "model_type": self.type,
            "model_label": self.label,
            "model_version": self.version,
        }
        return model_dict

    def to_default_dict(self):
        default_dict = {
            "default_id": self.id,
            "default_define": self.define_path,
            "default_weight": self.weight_path,
            "default_width": self.width,
            "default_height": self.height,
            "is_default": self.is_default
        }
        return default_dict

    @staticmethod
    def insert_default():
        init_model = [{'id':1, 'name':'keras', 'description':'vgg16', 'frame':1, 'type':1, 'define_path': 'vgg16',
                       'weight_path': 'vgg16_weights_tf_dim_ordering_tf_kernels_notop.h5', 'label':1, 'is_default':1},
                      {'id':2, 'name':'keras', 'description':'resnet50', 'frame':1, 'type':1, 'define_path': 'resnet50',
                       'weight_path': 'resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5', 'label':2, 'is_default':1},
                      {'id':3, 'name':'caffe', 'description':'vgg16', 'frame':2, 'type':1, 'define_path': 'vgg16',
                       'weight_path': 'vgg16net', 'label':3, 'is_default':1},
                      {'id':4, 'name':'caffe', 'description':'resnet50', 'frame':2, 'type':1, 'define_path': 'resnet50',
                       'weight_path': 'resnet50net', 'label':4, 'is_default':1}]
        for row in init_model:
            obj = Models(id=row['id'], name=row['name'], description=row['description'], frame=row['frame'], type=row['type'],
                         define_path=row['define_path'], weight_path=row['weight_path'], label=row['label'], is_default=row['is_default'])
            db.session.add(obj)
            db.session.commit()


    @staticmethod
    def from_json_default(json_model):
        model = Models.query.filter_by(id=json_model.get('default_id')).first()
        if model is None:
            return None
        name = json_model.get('name')
        description = json_model.get('description')
        label = json_model.get('label')
        frame = model.frame
        type = model.type
        define_path = model.define_path
        weight_path = model.weight_path
        if not all([name, frame, type, define_path, weight_path, label]):
            return None
        if not isinstance(label, int) or label <= 0:
            return None
        return Models(name=name, description=description, frame=frame, type=type,
                      define_path=define_path, weight_path=weight_path, width=width,
                      height=height, label=label)

    @staticmethod
    def from_json(json_model):
        name = json_model.get('name')
        description = json_model.get('description')
        frame = json_model.get('frame')
        type = json_model.get('type')
        define_path = json_model.get('define_path')
        weight_path = json_model.get('weight_path')
        label = json_model.get('label')
        if not all([name, frame, type, define_path, weight_path, label]):
            return None
        if not isinstance(label, int) or label <= 0:
            return None
        return Models(name=name, description=description, frame=frame, type=type,
                      define_path=define_path, weight_path=weight_path, width=width,
                      height=height, label=label)


