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



    DATAEXIST           = "3"
    LOGINERR            = "4102"
    USERERR             = "4104"

    PWDERR              = "4106"
    REQERR              = "4201"
    IPERR               = "4202"
    THIRDERR            = "4301"
    IOERR               = "4302"
    SERVERERR           = "4500"
    UNKOWNERR           = "4501"

error_map = {
    RET.OK                    : u"成功",
    RET.PARAMERR              : u"参数错误",
    RET.DBERR                 : u"数据库查询错误",
    RET.DATAERR               : u"数据错误",
    RET.SESSIONERR            : u"用户未登录",
    RET.NODATA                : u"无数据",
    RET.ROLEERR               : u"用户身份错误",
    RET.AUTHERR               : u"权限不足",


    RET.DATAEXIST             : u"数据已存在",


    RET.LOGINERR              : u"用户登录失败",

    RET.USERERR               : u"用户不存在或未激活",

    RET.PWDERR                : u"密码错误",
    RET.REQERR                : u"非法请求或请求次数受限",
    RET.IPERR                 : u"IP受限",
    RET.THIRDERR              : u"第三方系统错误",
    RET.IOERR                 : u"文件读写错误",
    RET.SERVERERR             : u"内部错误",
    RET.UNKOWNERR             : u"未知错误",
}