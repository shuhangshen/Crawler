import logging
import os
from pybloom_live import BloomFilter
from scrapy.exceptions import DropItem

from .tools import get_function_name
from .setting import ALLOW_SPIDER, DATA_PATH

logger = logging.getLogger()
base_path = DATA_PATH

# 文本 pipeline


class BloomCheckPipeline(object):
    def __init__(self):
        self.file_name = 'C:/Users/YJY/Desktop/workspace/dagongw/bloomfilter_takungpao.blm'
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


class WriteFilePipeline(object):
    """
    确认Field 参数
    field
    title
    url
    content
    保存文件 pipeline
    """

    accept_spider = ALLOW_SPIDER

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

        save_path = DATA_PATH
        if "spider" in item:
            save_path = os.path.join(save_path, item['spider'])
        dir_path = os.path.join(save_path, item['field'])

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
            for line in item['content']:
                try:
                    file.write(line + '\r\n')
                except Exception as reason:
                    print('Write content ERROR: %s' % reason)
        return item
