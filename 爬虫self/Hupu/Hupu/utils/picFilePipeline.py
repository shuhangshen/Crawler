import hashlib
import logging
import os

import time
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline

from veryins import settings

logger = logging.getLogger()

# 图片pipeline

class PicFilePipeline(ImagesPipeline):
    another_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Connection": "keep-alive",
        "Host": "www.veryins.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; W…) Gecko/20100101 Firefox/66.0",
    }

    def get_media_requests(self, item, info):
        category = item['category']
        urls = item['urls']

        for url in urls:
            logger.info("current download  {}".format(url))
            yield Request(url=url, meta={
                'category': category,
            }, headers=self.another_headers)

    def file_path(self, request, response=None, info=None):
        url = request.url

        file_path = time.strftime("%Y%m%d")
        + os.sep + request.meta['category']

        # 子文件夹创建
        image_store = settings.IMAGES_STORE
        category_path = os.path.join(image_store, file_path)
        print("category path:   ", category_path)
        if not os.path.exists(category_path):
            os.makedirs(category_path)

        # 返回文件名
        md5_hex = hashlib.new('md5', url.encode(encoding='utf-8')).hexdigest()
        file_path += os.sep + md5_hex + '.jpg'

        # file_path = hashlib.new('md5', url.encode(encoding='utf-8')).hexdigest() + '.jpg'
        logger.info("current save path  {}".format(file_path))
        return file_path

    def item_completed(self, results, item, info):
        return item

    def parse_test(self, response):
        logger.info(response.url)
