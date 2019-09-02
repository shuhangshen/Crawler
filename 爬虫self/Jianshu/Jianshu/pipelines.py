# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import datetime


class JianshuPipeline(object):
    def __init__(self):
        self.save_dir = 'Z:/data/Jianshu/'

    def save_file(self, item, spider):
        today_d = datetime.datetime.now().strftime('%Y%m%d')
        path = ''.join([self.save_dir, today_d, '/', item['author']])
        if not os.path.exists(path):
            os.makedirs(path)
        name = ''.join([path, '/', item['title'], '.txt'])
        with open(name, 'w', encoding='utf-8') as file:
            file.write(item['title'] + '\r\n')
            file.write(item['url'] + '\r\n')
            for line in item['content']:
                file.write(line + '\r\n')

    def process_item(self, item, spider):
        self.save_file(item, spider)
        return item
