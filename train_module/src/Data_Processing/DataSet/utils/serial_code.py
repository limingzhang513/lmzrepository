# -*- coding:utf-8 -*-

class RET:
    OK                  = "0"
    PARAMERR            = "1"
    DBERR               = "2"
    DATAERR             = "3"
    SESSIONERR          = "4"
    NODATA              = "5"
    ROLEERR             = "6"
    AUTHERR             = "7"

error_map = {
    RET.OK                    : u"成功",
    RET.PARAMERR              : u"参数错误",
    RET.DBERR                 : u"数据库查询错误",
    RET.DATAERR               : u"数据错误",
    RET.SESSIONERR            : u"用户未登录",
    RET.NODATA                : u"无数据",
    RET.ROLEERR               : u"用户身份错误",
    RET.AUTHERR               : u"权限不足",
}