# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import hashlib
import datetime
import logging
import scrapy
import urllib.request
import re
from scrapy.http import Request
from scrapy.pipelines.images import ImagesPipeline

from scrapy.exceptions import DropItem
#from pybloom_live import BloomFilter
logger = logging.getLogger('SaveImagePipeline')


# 继承ImagePipeline类,这是图片管道
class SaveImagePipeline(ImagesPipeline):
    match_char = re.compile(r'[?/\\":*<>|]+')
    default_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, sdch, br',
        'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    }

    #修改图片名称
    def file_path(self, request, response=None, info=None):
        #返回文件名
        item = request.meta['item']
        # name = request.meta['name']
        name = item['name']
        image_guid = re.sub(self.match_char, '-', request.url.split('/')[-1])
        filename = 'picture/{}/{}'.format(name, image_guid)
        return filename

    # 下载图片,imagepipeline根据image_urls中指定的url进行爬取，可以通过get_media_requests为每一个url生成一个Request
    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            # self.default_headers['referer'] = image_url
            yield Request(url=image_url, headers=self.default_headers, meta={"item": item})

    #图片下载完成后，处理结果会以二元组的方式返回给item_completed(),结果存在results中
    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        # image_paths = results[0][1].get('path')
        if not image_paths:
            raise DropItem('下载失败')
        logger.debug('下载图片成功')
        item['image_paths'] = image_paths
        print(item)
        return item

'''
class BloomCheckPipeline(object):
    def __init__(self):
        self.file_name = r'Z:/朱靖/布隆滤波器过滤文件/carpicture/BloomFiltercnki.blm'
        self.bf = None
        self.cap_begin = 0
        self.cap_end = 0
        self.cnt = 0

    def open_spider(self, spider):
        if os.path.exists(self.file_name):
            self.bf = BloomFilter.fromfile(open(self.file_name, 'rb'))
            self.cap_begin = len(self.bf)  # 打开blm文件时读入初始数量
            print('open blm file success')
            print('初始容量:%d' % self.cap_begin)
        else:
            self.bf = BloomFilter(100000000, 0.001)
            print('Not find the blm file, creat one')

    def process_item(self, item, spider):
        if item['image_url'] in self.bf:
            print('drop one item %s for exist' % item['title'])
            raise DropItem('drop an item %s for exists' % item['title'])
        else:
            try:
                self.bf.add(item['image_url'])
                self.cnt += 1
            except Exception as reason:
                print('BloomFilter Error------:%s' % reason)
            # 每写入1w个url时就保存blm文件一次
            if self.cnt > 10000:
                self.save_blm()
                self.cnt = 0
            return item

    def save_blm(self):
        print('Save Blm File ******')
        self.cap_end = len(self.bf)
        print('此次存入图片数量:%d' % (self.cap_end-self.cap_begin))
        self.bf.tofile(open(self.file_name, 'wb'))

    def close_spider(self, spider):
        print('close_spider tofile------')
        self.cap_end = len(self.bf)
        print('此次存入图片数:%d' % (self.cap_end-self.cap_begin))
        self.bf.tofile(open(self.file_name, 'wb'))
'''


class CarpicturePipeline(object):
    def __init__(self):
        self.save_dir = 'Z:/data/carpicture/'
        self.cnt = 0

    def save_file(self, item, spider):
        self.cnt += 1
        today_d = datetime.datetime.now().strftime('%Y%m%d')
        today_m = datetime.datetime.now().strftime('%Y%m%d%H')
        path = ''.join([self.save_dir, today_d, '/', item['title']])
        if not os.path.exists(path):
            os.makedirs(path)
        name = ''.join([path, '/T', today_m, 'N', str(self.cnt), '.jpg'])
        for image_url in item['image_urls']:
            urllib.request.urlretrieve(image_url, name)

    def process_item(self, item, spider):
        self.save_file(item, spider)
        return item
