# -*- coding:utf-8 -*-
import os
import re
import urllib
import urllib2
import urllib3
import urllib3.request
import json
import socket
# 设置超时
import time

timeout = 5
socket.setdefaulttimeout(timeout)


class Crawler:
    # 睡眠时长
    __time_sleep = 0.1
    __amount = 0
    __start_amount = 0
    __counter = 0
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}

    # 获取图片url内容等
    # t 下载图片时间间隔
    def __init__(self, t=0.1):
        self.time_sleep = t

    # 保存图片
    def __save_image(self, rsp_data, n):

        image_spider_list = list()

        # if not os.path.exists("./" + word):
        #     os.mkdir("./" + word)
        # 判断名字是否重复，获取图片长度
        # self.__counter = len(os.listdir('./' + word)) + 1
        for image_info in rsp_data['imgs']:
            try:
                time.sleep(self.time_sleep)
                print(image_info['objURL'])
                image_spider_list.append(image_info['objURL'])
                # fix = self.__get_suffix(image_info['objURL'])
                # urllib.urlretrieve(image_info['objURL'], './' + word + '/' + word + str(self.__counter) + str(fix))

            except urllib3.exceptions.HTTPError as urllib_err:
                print(urllib_err)
                continue
            except Exception as err:
                time.sleep(1)
                print(err)
                print("产生未知错误，放弃保存")
                continue
            else:
                print("图+1,已有" + str(self.__counter) + "张图")
                self.__counter += 1
                if len(image_spider_list) == n:
                    return image_spider_list

        return image_spider_list

    # 获取后缀名
    @staticmethod
    def __get_suffix(name):
        m = re.search(r'\.[^\.]*$', name)
        if m.group(0) and len(m.group(0)) <= 5:
            return m.group(0)
        else:
            return '.jpeg'

    # 获取前缀
    @staticmethod
    def __get_prefix(name):
        return name[:name.find('.')]

    # 开始获取
    def __get_images(self, word='火', n=0):
        spider_list = []
        search = urllib.quote(word)
        # pn int 图片数
        pn = self.__start_amount
        retry = 0
        while pn < self.__amount and retry < 20:

            url = 'http://image.baidu.com/search/avatarjson?tn=resultjsonavatarnew&ie=utf-8&word=' + search + '&cg=girl&pn=' + str(
                pn) + '&rn=60&itg=0&z=0&fr=&width=&height=&lm=-1&ic=0&s=0&st=-1&gsm=1e0000001e'
            # 设置header防ban
            try:
                time.sleep(self.time_sleep)
                req = urllib2.Request(url=url, headers=self.headers)
                page = urllib2.urlopen(req)
                rsp = page.read().decode('unicode_escape')
            except UnicodeDecodeError as e:
                print(e)
                print('-----UnicodeDecodeErrorurl:', url)
                retry += 1
            except socket.timeout as e:
                print(e)
                print("-----socket timout:", url)
                break
            except Exception as e:
                print(e)
                print("-----Exception:", url)
                break
            else:
                # 解析json
                rsp_data = json.loads(rsp)
                # print(rsp_data)
                spider_list = self.__save_image(rsp_data, n)
                # 读取下一页
                print("下载下一页")
                pn += 60
                page.close()
            finally:
                pass
        print("下载任务结束")
        # print(spider_list)
        return spider_list

    def start(self, word, spider_page_num=1, start_page=1, n=0):
        """
        爬虫入口
        :param word: 抓取的关键词
        :param spider_page_num: 需要抓取数据页数 总抓取图片数量为 页数x60
        :param start_page:起始页数
        :return:
        """

        word = word.encode('utf-8')

        self.__start_amount = (start_page - 1) * 60
        self.__amount = spider_page_num * 60 + self.__start_amount
        spider_response_list = self.__get_images(word, n)
        # print(spider_response_list)
        return spider_response_list


if __name__ == '__main__':
    crawler = Crawler(0.05)
    crawler.start('fire', 1, 1, 50)
