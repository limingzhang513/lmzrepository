# -*- coding: utf-8 -*-
from . import fdfs_redis_dbs
from fdfs_client.client import *
from DataSet.fastdfs.config import RedisError
import redis
import time
import random
import logging
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class Fdfs(object):

    def __init__(self):
        """conf_file:配置文件"""
        # self.client = FastClient()
        self.client = Fdfs_client()  # 可以设定参数conf_path=配置路径
        self.fdfs_redis = []
        for i in fdfs_redis_dbs:  # 存在两个redis数据库，8和9
            self.fdfs_redis.append(redis.Redis(host=i[0], port=i[1], db=i[2]))

    def upload(self, upload_file, filename=None, file_ext_name=None):
        """
        buffer存储文件
        参数：
        filename:自定义文件名，如果不指定，将远程file_id作为文件名
        返回值：
        {
        'group':组名,
        'file_id':不含组名的文件ID,
        'size':文件尺寸,
        'upload_time':上传时间
        }
        """
        if filename and random.choice(self.fdfs_redis).exists(filename):
            logging.info('File(%s) exists.' % filename)
            return random.choice(self.fdfs_redis).hgetall(filename)
        t1 = time.time()
        try:
            ret_dict = self.client.upload_by_buffer(upload_file, file_ext_name)  # 文件上传buffer至redis
        except Exception as e:
            logging.error('Error occurred while uploading: %s' % e.message)
            return None
        t2 = time.time()
        # logging.info('Upload file(%s) by buffer, time consume: %fs' % (filename, (t2 - t1)))
        for key in ret_dict:
            logging.debug('[+] %s : %s' % (key, ret_dict[key]))
        stored_filename = ret_dict['Remote file_id']
        stored_filename_without_group = stored_filename[stored_filename.index('/') + 1:]
        if not filename:
            filename = stored_filename_without_group
        vmp = {'group': ret_dict['Group name'], 'file_id': stored_filename_without_group,
               'size': ret_dict['Uploaded size'], 'upload_time': int(time.time() * 1000),
               'filename': filename, 'group_file_id': ret_dict['Remote file_id']}
        try:
            for i in self.fdfs_redis:  # 查看redis是否保存成功
                if not i.hmset(filename, vmp):
                    raise RedisError('Save Failure')
                # logging.info('Store file(%s) by buffer successful' % filename)
        except Exception as e:
            logging.error('Save info to Redis failure. rollback...%s' % e.message)
            try:
                ret_dict = self.client.delete_file(stored_filename)
            except Exception as e:
                logging.error('Error occurred while deleting: %s' % e.message)
            return None
        return vmp

    def uploads(self, upload_file, filename=None):
        """
        路径存储文件
        参数：
        filename:自定义文件名，如果不指定，将远程file_id作为文件名
        返回值：
        {
        'group':组名,
        'file_id':不含组名的文件ID,
        'size':文件尺寸,
        'upload_time':上传时间
        }
        """
        if filename and random.choice(self.fdfs_redis).exists(filename):
            logging.info('File(%s) exists.' % filename)
            return random.choice(self.fdfs_redis).hgetall(filename)
        t1 = time.time()
        try:
            ret_dict = self.client.upload_by_filename(upload_file)
        except Exception as e:
            logging.error('Error occurred while uploading: %s' % e.message)
            return None
        t2 = time.time()
        # logging.info('Upload file(%s) by buffer, time consume: %fs' % (filename, (t2 - t1)))
        for key in ret_dict:
            logging.debug('[+] %s : %s' % (key, ret_dict[key]))
        stored_filename = ret_dict['Remote file_id']
        stored_filename_without_group = stored_filename[stored_filename.index('/') + 1:]
        if not filename:
            filename = stored_filename_without_group
        vmp = {'group': ret_dict['Group name'], 'file_id': stored_filename_without_group,
               'size': ret_dict['Uploaded size'], 'upload_time': int(time.time() * 1000),
               'filename': filename, 'group_file_id': ret_dict['Remote file_id']}
        try:
            for i in self.fdfs_redis:
                if not i.hmset(filename, vmp):
                    raise RedisError('Save Failure')
                # logging.info('Store file(%s) by buffer successful' % filename)
        except Exception as e:
            logging.error('Save info to Redis failure. rollback...%s' % e.message)
            try:
                ret_dict = self.client.delete_file(stored_filename)  # 删除保存的文件名
            except Exception as e:
                logging.error('Error occurred while deleting: %s' % e.message)
            return None
        return vmp

    def remove(self, filename):
        """
        删除文件,
        filename是用户自定义文件名
        return True|False
        """
        fileinfo = random.choice(self.fdfs_redis).hgetall(filename)
        stored_filename = '%s/%s' % (fileinfo['group'], fileinfo['file_id'])
        try:
            ret_dict = self.client.delete_file(stored_filename)
            logging.info('Remove stored file successful')
        except Exception as e:
            logging.error('Error occurred while deleting: %s' % e.message)
            return False
        for i in self.fdfs_redis:
            if not i.delete(filename):
                logging.error('Remove fileinfo in redis failure')
        logging.info('%s removed.' % filename)
        return True

    def download(self, filename):
        """
        下载文件cat is not exists
        返回二进制
        """
        finfo = self.getInfo(filename)
        if finfo:
            ret = self.client.download_to_buffer('%s/%s' % (finfo['group'], finfo['file_id']))
            return ret['Content']
        else:
            logging.debug('%s is not exists' % filename)
            return None

    # def download(self, download_file, file_id):
    #     try:
    #         ret_download = self.client.download_to_file(download_file, file_id)
    #         print ret_download
    #         return ret_download
    #
    #     except Exception as e:
    #         print e
    #         logging.warning(u'图片下载失败，错误信息：%s' % e.message)
    #         return None

    def list(self, pattern='*'):
        """列出文件列表"""
        return random.choice(self.fdfs_redis).keys(pattern)

    def getInfo(self, filename):
        """
        获得文件信息
        return:{
        'group':组名,
        'file_id':不含组名的文件ID,
        'size':文件尺寸,
        'upload_time':上传时间
        }
        """
        return random.choice(self.fdfs_redis).hgetall(filename)  # 哈希获取所有redis中的文件名 ：字段和名


fun = Fdfs()
