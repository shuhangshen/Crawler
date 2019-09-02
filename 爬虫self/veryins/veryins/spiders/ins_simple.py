# -*- coding: utf-8 -*-
import copy
import json
import logging
import re
import time

import os
import scrapy
from scrapy import Request
from scrapy.crawler import CrawlerProcess

from veryins.utils.try_except import try_except
from veryins.settings import REDIS_HOST, REDIS_PORT
from veryins.utils.redis_helper import RedisHelper
from veryins.utils.tools import get_function_name, print_html_body

logger = logging.getLogger()
redis_helper = RedisHelper(host=REDIS_HOST, port=REDIS_PORT)
VERYINS_LIST = "VERYINS_LIST"


class InsSimpleSpider(scrapy.Spider):
    name = 'ins_simple'
    allowed_domains = ['veryins.com']
    start_urls = ['https://www.veryins.com/']

    host = r'https://www.veryins.com/'

    def parse(self, response):
        """
        加载第一页,并循环翻页
        :param response:
        :return:
        """
        logger.info("{} Url {}".format(get_function_name(), response.url))
        data_code = response.xpath('//div/@data-code').extract()
        for code in data_code:
            url = self.host + "p/{}".format(code)
            # cursor = response.xpath("//div[@id='list']/@next-cursor").extract_first()
            # url = self.host + str(cursor)
            # print("*********{}********".format(url))
            yield Request(url=url, method='POST', callback=self.parse_user_info)
        for i in range(2, 13):
            url = 'https://www.veryins.com/user?cid={}'.format(i)
            try:
                yield Request(url=url, method='GET', callback=self.parse_list)
            except Exception as e:
                logger.error("{} failed as reason: {}".format(url, e))

    def parse_list(self, response):
        links = response.xpath('//div[@class="search-users "]/a/@href').extract()
        for link in links:
            user_name = re.findall(r'/(.*?)', link)[0]
            url = self.host + user_name
            try:
                yield Request(url=url, method='GET', meta={'user_name': user_name}, callback=self.parse_user_page)
            except Exception as e:
                logger.error("{} failed as reason: {}".format(url, e))
    '''
    @try_except
    def parse_list(self, response):
        """
        加载更多分页
        :param response:
        :return:
        """
        logger.info("{} Url {}".format(get_function_name(), response.url))

        dat = json.loads(response.body)
        print(response.text)

        # 解析分页中的用户
        top_posts = dat['top_posts']
        for item in top_posts:
            code = item['code']
            url = self.host + "p/{}".format(code)
            yield Request(url=url, method='POST', callback=self.parse_user_info)

        # 加载更多分页
        has_next_page = dat['page_info']['has_next_page']
        if has_next_page:
            cursor = dat['next']
            url = self.host + str(cursor)
            yield Request(url=url, method='POST', callback=self.parse_list)
    '''

    @try_except
    def parse_user_info(self, response):
        """
        提取用户信息
        :param response:
        :return:
        """
        logger.info("{} Url {}".format(get_function_name(), response.url))
        dat = json.loads(response.body)

        # 请求用户主页
        user_name = dat['owner']['username']
        url = self.host + user_name

        yield Request(url=url, method='GET', callback=self.parse_user_page,
                      meta={
                          'user_name': user_name
                      })

    @try_except
    def parse_user_page(self, response):
        logger.info("{} Url {}".format(get_function_name(), response.url))

        # 加载分页需要信息
        category = response.meta['user_name']
        # user_tid = response.xpath("//*[@id='username']/@data-uid").extract_first()
        cursor = response.xpath("//*[@id='list']/@next-cursor").extract_first()

        # 图片pipeline
        image_urls = response.xpath("//div[@class='item']/div/@data-src").extract()
        item = dict()
        item['category'] = category
        item['urls'] = [url for url in image_urls if not url.startswith(r'/images')]
        # item['urls'] = image_urls
        seq_item = json.dumps(item)
        redis_helper.list_insert(key=VERYINS_LIST, elem=seq_item)

        meta = {
            'category': category,
            # 'user_tid': user_tid,
            'cursor': cursor,
        }
        if cursor is None:
            return
        # 下一页
        url = r'https://www.veryins.com/user/{user}?next={cursor}&uid=&rg=' \
            .format(user=category,
                    cursor=cursor,
                    )
        yield Request(url=url, method='POST', callback=self.parse_user_page_more,
                      meta=meta)

    @try_except
    def parse_user_page_more(self, response):
        logger.info("{} Url {}".format(get_function_name(), response.url))

        dat = json.loads(response.body)
        category = response.meta['category']
        # user_tid = response.meta['user_tid']

        # 图片pipeline
        nodes = dat['user']['media']['nodes']

        item = dict()
        item['category'] = category
        item['urls'] = [node['display_src'] for node in nodes]
        seq_item = json.dumps(item)
        redis_helper.list_insert(key=VERYINS_LIST, elem=seq_item)

        # 查找分页
        has_next_page = dat['user']['media']['page_info']['has_next_page']
        if has_next_page:
            cursor = dat['user']['media']['page_info']['end_cursor']

            url = r'https://www.veryins.com/user/{user}?next={cursor}&uid=&rg=' \
                .format(user=category,
                        cursor=cursor,
                        )
            meta = copy.deepcopy(response.meta)
            meta['cursor'] = cursor

            yield Request(url=url, method='POST', callback=self.parse_user_page_more,
                          meta=meta)
            time.sleep(0.1)


def run():
    process = CrawlerProcess()
    process.crawl(InsSimpleSpider)
    process.start()


if __name__ == '__main__':
    # run()
    os.system('scrapy crawl ins_simple')
