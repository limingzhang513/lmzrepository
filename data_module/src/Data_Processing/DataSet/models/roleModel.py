# -*- coding:utf-8 -*-
from DataSet import db


class Permission:
    UPDATE = 1
    CRUD = 2
    ADMINISTER = 4


class Role(db.Model):
    __tablename__ = 'roles'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)   # 用户默认角色,default是False
    permissions = db.Column(db.Integer)  # 用户权限设置，是一个数值
    # lazy='dynamic'表示表Role对象点users属性，返回的是对象，仍可进行过滤等相关操作，默认lazy='select'
    users = db.relationship('User', backref='role', lazy='dynamic')  # lazy='select'时查询的时对应User表的结果

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.UPDATE,),  # 权限为1
            'Moderator': (Permission.UPDATE, Permission.CRUD),  # 权限 1，2
            'Administrator': (Permission.UPDATE, Permission.CRUD, Permission.ADMINISTER)  # 权限 1，2，4
        }

        default_role = 'User'
        for r in roles:  # 通过角色查找现有角色去设置权限，方便修改权限和添加新角色
            role = Role.query.filter_by(name=r).first()
            if role is None:  # 当数据库中没有某个角色时创建个新角色，并添加user权限
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:  # 遍历 User对应的权限元组
                role.add_permission(perm)
            role.default = (role.name == default_role)  # 判断是不是默认用户
            db.session.add(role)
        db.session.commit()

    def has_permission(self, perm):  # 判断当前角色是否已经有该权限
        return self.permissions & perm == perm

    def add_permission(self, perm):  # 角色添加权限
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permiss(self, perm):  # 角色删除权限
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):  # 重置角色
        self.permissions = 1
# python manage.py shell
# from DataSet.models.roleModel import Role
# Role.insert_roles()
# Role.query.all()

# FLUSHALL
# sudo netstat -apn |grep 5000
# redis-cli --raw -h 192... -p 6379 -a 123456
