# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import inspect
import logging

import os


def get_function_name():
    """
    获取当前执行函数名
    :param self:
    :return:
    """
    return inspect.stack()[1][3]


class HaiwainetPipeline(object):
    def process_item(self, item, spider):
        return item


logger = logging.getLogger()
current_spider_name = "haiwai"
base_path = os.path.join(r'Z:\lisi8\WORKSPACE', r'haiwainet')


class WriteFilePipeline(object):
    accept_spider = [
        current_spider_name
    ]

    def __make_dir(self, path):
        """
        Make_Dir
        """
        if not os.path.exists(path):
            os.makedirs(path)

    def process_item(self, item, spider):
        if spider.name not in self.accept_spider:
            logger.info("failue spider [name] {} ".format(spider.name))
            return

        dir_path = os.path.join(base_path, item['field'])
        self.__make_dir(dir_path)
        save_file_path = dir_path + os.path.sep + item['title'] + '.txt'
        logger.info("{}  save:   {}".format(get_function_name()
                                            , save_file_path))
        # 已按路径保存的文件
        if os.path.exists(save_file_path):
            logger.info("{} item exist".format(get_function_name()))
            return item

        logger.info("current save path  {}".format(save_file_path))
        with open(save_file_path, 'w', encoding='utf-8') as file:
            file.write(item['url'] + '\r\n')
            file.write(item['title'] + '\r\n')
            file.write(item['content'])

        return item
