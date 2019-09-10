# -*- coding:utf-8 -*-
from DataSet import db
from DataSet.models.baseModel import BaseModel


class Version(BaseModel, db.Model):
    """版本"""

    __tablename__ = "ds_versions"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 版本编号
    collection_id = db.Column(db.Integer, db.ForeignKey('ds_collections.id'), nullable=False)
    name = db.Column(db.String(32), nullable=False)  # 版本名称
    description = db.Column(db.String(128))  # 版本描述
    zip_path = db.Column(db.String(64))  # 版本地址
    average_number = db.Column(db.Integer, default=0)  # 平均框值
    mean_size = db.Column(db.String(16), default='0*0')  # 平均大小
    label_info = db.Column(db.String(512))  # 标签使用详情
    images = db.relationship("Image", backref="version")  # 版本/图片一对多

    def to_dict(self):
        """将对象转换为字典数据"""

        version_dict = {
            "version_id": self.id,
            "version_name": self.name,
            "version_description": self.description,
            "version_average_number": self.average_number,
            "version_mean_size": self.mean_size
        }
        return version_dict
