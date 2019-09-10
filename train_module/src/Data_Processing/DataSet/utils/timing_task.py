# !/usr/bin/python2
# -*- coding:utf-8 -*-

'''
# 1.get all req num {task_id: lines, 600: 112, ...}
with open("logfile.server.log", 'r') as f
    for l in f.readlines()
        re: '*-*req is coming:600*-*'
        req_dict.update({600: 112}) (if not exists)

# 2.create log_path - lines dict just like {"log_path":[1, 500], ...}
                                                      (start, end)
for num in req_list
    for l in f.readlines()
        if re == num
        start_lines = lines(num)
        log_path = lines + 1 (split handle)
        re: if '*-*all of complete:%s*-*'
            if '*-*err stop:%s*-*'
            if '*** Check failure stack trace: ***'
        end_lines = lines(num)
        log_file_dict.update({log_path:[start_lines, end_lines]})

# 3.create user's server.log file

for k, v in log_file_dict.items()
    if k is exists:
        continue
    with open("logfile.server.log", 'r') as rf
        cont = cut start to end
    with open(k, 'w') as wf
        wf.write(cont)


remember like:
'''

import os
import re
import time
import requests
import schedule
import threading

CAFE_LOG = '/home/duduo/workspace/cmcc/China-Mobile/Data_Processing/logs/caffe_server.log'
KERAS_LOG = '/home/duduo/workspace/cmcc/China-Mobile/Data_Processing/logs/keras_server.log'


def log_handler(supervisor_log):
    '''
    handle supervisor-server.log and create user's server.log file
    :return:
    '''
    req_dict = get_all_req(supervisor_log)
    log_file_dict = create_log_dict(req_dict, supervisor_log)
    create_log_file(log_file_dict, supervisor_log)
    print req_dict
    print log_file_dict


def get_all_req(supervisor_log):
    '''
    get all req task_id
    :return: req_dict {task_id: lines, 600: 112, ...}
    '''
    req_dict = dict()
    with open(supervisor_log, 'r') as rf:
        for line, cont in enumerate(rf):
            num = re.findall('\*-\*req is coming:(\d+)\*-\*', cont, re.M)
            if num:
                req_dict.update({num[0]: line + 1})
    return req_dict


def create_log_dict(req_dict, supervisor_log):
    '''
    create log_path - lines dict

    :param req_dict:
    :return: log_file_dict {"log_path":[1, 500], ...}
                                     (start, end)
    '''
    log_file_dict = dict()
    for num, start_line in req_dict.items():
        with open(supervisor_log, 'r') as rf:
            trained_path = None
            end_line = start_line
            for cont in rf.readlines()[start_line-1:]:
                end_line += 1
                _path = re.findall('\*-\*trained_dir:(\S+)\*-\*', cont, re.M)
                if _path and os.path.exists(_path[0]):
                    log_path = os.path.join(_path[0], 'log', 'train_log.log')
                    try:
                        r = requests.post(url='http://127.0.0.1:5000/api/update_log_info',
                                          json={'_path': _path[0], 'log_path': log_path})
                    except Exception:
                        print 'log_path info update fail'
                    log_file_dict.update({log_path: [start_line]})
                    trained_path = log_path
                _end = re.findall('\*-\*all of complete:%s\*-\*' % num, cont, re.M)
                if _end:
                    log_file_dict[trained_path].append(end_line - 1)
                    break
                _end = re.findall('\*-\*err stop:%s\*-\*' % num, cont, re.M)
                if _end:
                    log_file_dict[trained_path].append(end_line - 1)
                    break
                _end = re.findall('\*\*\* Check failure stack trace: \*\*\*', cont, re.M)
                if _end:
                    log_file_dict[trained_path].append(end_line - 1)
                    break
    return log_file_dict


def create_log_file(log_file_dict, supervisor_log):
    '''
    create user's server.log file
    :param log_file_dict:
    :return:
    '''
    for log_path, index in log_file_dict.items():
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                _cont = f.readline()
                if _cont:
                    continue
        if not isinstance(index, list):
            continue
        if len(index) == 0:
            continue
        if len(index) < 2:
            index.append(index[0])
        rf = open(supervisor_log)
        wf = open(log_path, 'w')
        for line in rf.readlines()[index[0]-1: index[1]]:
            wf.write(line)
        wf.close()
        rf.close()


def send_del_command(flag=1):
    try:
        if flag == 1:
            _ = requests.post(url='http://127.0.0.1:5000/api/del_expire_info', json={'flag': flag})
        if flag == 2:
            _ = requests.post(url='http://127.0.0.1:5000/api/del_expire_info', json={'flag': flag})
    except Exception:
        print 'del expire info fail'


def keras_log_thread():
    print 'start synchronize <keras> supervisor server.log to user\'s server.log file at %s' % time.strftime('%Y-%m-%d', time.localtime(time.time()))
    threading.Thread(target=log_handler, args=(KERAS_LOG,)).start()


def caffe_log_thread():
    print 'start synchronize <caffe> supervisor server.log to user\'s server.log file at %s' % time.strftime('%Y-%m-%d', time.localtime(time.time()))
    threading.Thread(target=log_handler, args=(CAFE_LOG,)).start()


def del_expire_dataset():
    threading.Thread(target=send_del_command, args=(1,)).start()


def del_expire_result():
    threading.Thread(target=send_del_command, args=(2,)).start()


def run_log_synchronization_schedule():
    schedule.every(5).minutes.do(keras_log_thread)
    schedule.every(5).minutes.do(caffe_log_thread)
    schedule.every().day.at("2:00").do(del_expire_dataset)
    schedule.every().day.at("2:00").do(del_expire_result)

    while 1:
        schedule.run_pending()
        time.sleep(60)


run_log_synchronization_schedule()

