# -*- coding:utf-8 -*-
from DataSet import db
from DataSet.models.baseModel import BaseModel


class Collection(BaseModel, db.Model):
    """集合"""

    __tablename__ = "ds_collections"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
    user_id = db.Column(db.Integer, db.ForeignKey('ds_users.id'), nullable=False)
    name = db.Column(db.String(32), nullable=False)  # 集合名字
    type = db.Column(db.Integer, default=1)  # 类型 (分类/人脸 | 检测/切割)
    desc = db.Column(db.String(128))  # 数据集描述
    images = db.relationship("Image", backref="collection")  # 集合/图片一对多
    versions = db.relationship("Version", backref="collection")  # 集合/版本一对多
    labels = db.relationship("Label", backref="collection")  # 集合/标签一对多

    parameter_1 = db.Column(db.String(32))
    parameter_2 = db.Column(db.Integer)

    def to_dict(self):
        """将对象转换为字典数据"""
        collection_dict = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "desc": self.desc,
        }

        return collection_dict
