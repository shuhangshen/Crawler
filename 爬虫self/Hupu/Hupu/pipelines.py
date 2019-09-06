# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import os
import logging
import scrapy
import urllib.request

from scrapy.http import Request
from scrapy.pipelines.images import ImagesPipeline
from pybloom_live import BloomFilter
from scrapy.exceptions import DropItem

logger = logging.getLogger()


class SaveImagePipeline(ImagesPipeline):
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
        # name = item['title']
        title = item['title']
        today_d = datetime.datetime.now().strftime('%Y%m%d')
        image_guid = request.url.split('/')[-1]
        filename = '{}/{}/{}/{}/{}/{}'.format(today_d, item['forum'], item['topic'], title, title, image_guid)
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


class HupuPipeline(object):
    def __init__(self):
        self.cnt = 0
        # self.save_dir = 'Z:/ssh/虎扑/'
        self.save_dir = 'Z:/data/虎扑/虎扑社区/'

    def save_file(self, item, spider):
        self.cnt += 1
        today_d = datetime.datetime.now().strftime('%Y%m%d')
        today_m = datetime.datetime.now().strftime('%Y%m%d%H')
        path = ''.join([self.save_dir, today_d, '/', item['forum'], '/', item['topic'], '/', item['title']])
        if not os.path.exists(path):
            os.makedirs(path)
        name = ''.join([path, '/', today_m, 'N', str(self.cnt), '.txt'])
        # name = ''.join([path, '/', str(self.cnt), '.txt'])
        with open(name, 'w', encoding='utf-8') as file:
            # file.write(item['title'] + '\r\n')
            file.write(item['url'] + '\r\n')
            for line in item['content']:
                file.write(line + '\r\n')

    def process_item(self, item, spider):
        self.save_file(item, spider)
        return item
