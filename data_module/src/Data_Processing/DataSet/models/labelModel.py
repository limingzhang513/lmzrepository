# -*- coding:utf-8 -*-
from DataSet import db
from DataSet.models.baseModel import BaseModel


class Label(BaseModel, db.Model):
    """标签"""

    __tablename__ = "ds_labels"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 标签编号
    collection_id = db.Column(db.Integer, db.ForeignKey('ds_collections.id'), nullable=True)  # 集合标签
    label_id = db.Column(db.Integer)  # 集合内的标签ID
    name = db.Column(db.String(32), nullable=False)  # 标签名称/类别
    count = db.Column(db.Integer, default=0)  # 标签使用量

    def to_dict(self):
        """将对象转换为字典数据"""

        label_dict = {
            "label_id": self.label_id,
            "label_name": self.name,
            "label_count": self.count
        }
        return label_dict
