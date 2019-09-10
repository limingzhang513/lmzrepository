# -*- coding:utf-8 -*-
from DataSet import db
from DataSet.models.baseModel import BaseModel


class Image(BaseModel, db.Model):
    """图片"""
    __tablename__ = "ds_images"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 图片编号
    version_id = db.Column(db.Integer, db.ForeignKey('ds_versions.id'), nullable=True)  # 版本图片
    collection_id = db.Column(db.Integer, db.ForeignKey('ds_collections.id'), nullable=False)  # 集合图片
    name = db.Column(db.String(128), nullable=False)  # 图片名称
    site = db.Column(db.String(128), nullable=False)  # 图片地址
    label_path = db.Column(db.String(128), nullable=True)  # 图片标注路径
    status = db.Column(db.Integer, default=0)  # 图片状态(是否标注)
    structured_path = db.Column(db.String(128), nullable=True)  # 图片结构化路径
    md5 = db.Column(db.String(32), index=True)

    def to_dict(self):
        """将对象转换为字典数据"""

        image_dict = {
            "id": self.id,
            "name": self.name,
            "site": self.site,
            "label_path": self.label_path,
            "state": self.state,
            "structured_path": self.structured_path
        }
        return image_dict
