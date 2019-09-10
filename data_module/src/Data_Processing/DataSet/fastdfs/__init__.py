# -*- coding: utf-8 -*-
# fastdfs tracker, multiple tracker supported
fdfs_tracker = {
'host_tuple':('localhost',),
'port':22122,
'timeout':30,
'name':'Tracker Pool'
}

# fastdfs meta db, multiple redisdb supported
fdfs_redis_dbs = (
    ('localhost', 6379, 9),
    ('localhost', 6379, 8)
)
