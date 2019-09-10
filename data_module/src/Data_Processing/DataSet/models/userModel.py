# -*- coding:utf-8 -*-
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from DataSet import db
from DataSet.models.shareModel import Share
from DataSet.models.baseModel import BaseModel
from DataSet.models.roleModel import Role, Permission


# 用户类
class User(db.Model, BaseModel):
    __tablename__ = 'ds_users'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 用户编号
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))  # ???
    shares_id = db.Column(db.Integer, db.ForeignKey('ds_shares.id'))  # 用户/分享集合一对一
    name = db.Column(db.String(32), unique=True, nullable=False)  # 用户昵称
    email = db.Column(db.String(128), index=True, unique=True)  # 邮箱
    password_hash = db.Column(db.String(128), nullable=False)  # 加密的密码
    login_time = db.Column(db.Integer)  # 登录时间验证
    collections = db.relationship("Collection", backref="user")  # 用户/集合一对多

    def __repr__(self):
        return '<User %r>' % self.name  # 实例化User类后，直接打印实例返回name属性，默认返回一个对象，现在是重写

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.name == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            elif self.email == current_app.config['ADMIN_EMAIL']:
                self.role = Role.query.filter_by(name='Administrator').first()
            else:
                self.role = Role.query.filter_by(default=True).first()

        if self.share is None:
            self.share = Share()

    @property
    def password(self):
        """获取password属性时被调用"""
        raise AttributeError("不可读")

    @password.setter
    def password(self, passwd):
        """设置password属性时被调用，设置密码加密"""
        self.password_hash = generate_password_hash(passwd)

    def check_password(self, passwd):
        """检查密码的正确性"""
        return check_password_hash(self.password_hash, passwd)

    # 查看用户是否有权限
    def can(self, permission):
        return self.role is not None and \
               (self.role.permissions & permission) == permission

    # 验证用户是否管理员
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @staticmethod
    def get(id):
        return User.query.filter_by(id=id).first()

    def add(self, user):
        db.session.add(user)
        return session_commit()

    def update(self):
        return session_commit()

    def delete(self, id):
        self.query.filter_by(id=id).delete()
        return session_commit()

    def to_dict(self):
        """将对象转换为字典数据"""
        user_dict = {
            "id": self.id,
            "name": self.name,
        }
        return user_dict


def session_commit():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        reason = str(e)
        return reason

    # # 生成更改邮箱密令
    # def change_email_token(self, email, expiration=3600):
    #     s = Serializer(current_app.config['SECRET_KEY'], expiration)
    #     return s.dumps({
    #         'newEmail': email,
    #         'id': self.id
    #     })
    #
    # # 验证更改邮箱密令
    # def change_email_confirm(self, token):
    #     s = Serializer(current_app.config['SECRET_KEY'])
    #     try:
    #         data = s.loads(token)
    #     except:
    #         return False
    #     if data.get('id') != self.id:
    #         return False
    #     self.email = data.get('newEmail')
    #     db.session.add(self)
    #     return True
