# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import os
from pybloom_live import BloomFilter
from scrapy.exceptions import DropItem


class BloomCheckPipeline(object):
    def __init__(self):
        self.file_name = 'C:/Users/YJY/Desktop/workspace/Guokr/bloomfilter_guokr.blm'
        self.bf = None
        self.cap_begin = 0
        self.cap_end = 0
        self.cnt = 0

    def open_spider(self, spider):
        if os.path.exists(self.file_name):
            self.bf = BloomFilter.fromfile(open(self.file_name, 'rb'))
            print('open blm file success')
            self.cap_begin = len(self.bf)
            print('open blm file success')
            print('初始容量:%d' % self.cap_begin)
        else:
            self.bf = BloomFilter(100000000, 0.001)
            print('Not find the blm file')

    def process_item(self, item, spider):
        if item['url'] in self.bf:
            print('drop one item %s for exits' % item['title'])
            raise DropItem('drop an item %s for exits' % item['title'])
        else:
            try:
                self.bf.add(item['url'])
                self.cnt += 1
            except Exception as reason:
                print("BloomFilter Error------:%s" % reason)
            if self.cnt > 10000:
                self.save_blm()
                self.cnt = 0
            return item

    def save_blm(self):
        print('Save Blm File ******')
        self.cap_end = len(self.bf)
        print('此次存入文章数:%d' % (self.cap_end - self.cap_begin))
        self.bf.tofile(open(self.file_name, 'wb'))

    def close_spider(self, spider):
        print('close spider tofile-------')
        self.cap_end = len(self.bf)
        print('此次存入文章数:%d' % (self.cap_end - self.cap_begin))
        self.bf.tofile(open(self.file_name, 'wb'))


class GuokrPipeline(object):
    def __init__(self):
        self.save_dir = 'Z:/data/Guokr/'

    def save_file(self, item, spider):
        title = item['title']
        field = item['field']
        fields = item['fields']
        today_d = datetime.datetime.now().strftime('%Y%m%d')
        path = ''.join([self.save_dir, today_d, '/', field])
        if fields == 'none':
            if not os.path.exists(path):
                os.makedirs(path)
            name = ''.join([path, '/', title, '.txt'])
            with open(name, 'w', encoding='utf-8') as file:
                file.write(item['title'] + '\r\n')
                file.write(item['url'] + '\r\n')
                for line in item['content']:
                    file.write(line + '\r\n')
        name1 = ''.join([path, '/', fields])
        if not os.path.exists(name1):
            os.makedirs(name1)
        name = ''.join([name1, '/', title, '.txt'])
        with open(name, 'w', encoding='utf-8') as file:
            file.write(item['title'] + '\r\n')
            file.write(item['url'] + '\r\n')
            for line in item['content']:
                file.write(line + '\r\n')

    def process_item(self, item, spider):
        self.save_file(item, spider)
        return item
