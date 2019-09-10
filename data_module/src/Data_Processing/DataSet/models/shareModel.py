# -*- coding:utf-8 -*-
from DataSet import db


class Share(db.Model):
    __tablename__ = "ds_shares"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    my_share = db.Column(db.String(128))  # 我的分享 "{1:[4,5,6], 2:[7,8]}"
    share_collection = db.Column(db.String(128))  # 被分享的数据集 "[1,2,3,4]"
    users = db.relationship('User', backref='share', uselist=False)  # 参数uselist=False 表示一对一

    def to_dict(self):
        """将对象转换为字典数据"""

        share_dict = {
            "share_collection": self.share_collection
        }
        return share_dict
