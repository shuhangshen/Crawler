# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import os


class DianpingPipeline(object):
    def __init__(self):
        self.cnt = 0
        # self.save_dir = 'Z:/data/大众点评/'
        self.save_dir = 'Z:/ssh/大众点评2/'

    def save_file(self, item, spider):
        # self.cnt += 1
        today_d = datetime.datetime.now().strftime('%Y%m%d')
        path = ''.join([self.save_dir, today_d, '/', item['shop']])
        if not os.path.exists(path):
            os.makedirs(path)
        name = ''.join([path, '/', item['users'], '.txt'])
        # name = ''.join([path, '/', str(self.cnt), '.txt'])
        with open(name, 'w', encoding='utf-8') as file:
            # file.write(item['title'] + '\r\n')
            file.write(item['url'] + '\r\n')
            for line in item['content']:
                file.write(line + '\r\n')

    def process_item(self, item, spider):
        self.save_file(item, spider)
        return item
