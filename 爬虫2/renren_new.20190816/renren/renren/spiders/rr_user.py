# -*- coding: utf-8 -*-
import json
import logging

import math
import traceback

import scrapy
import time
from bs4 import BeautifulSoup
from scrapy import Request
from scrapy.crawler import CrawlerProcess

from renren.settings import REDIS_HOST, REDIS_PORT, HOST_NAME
from renren.utils.redis_helper import RedisHelper
from renren.utils.setting import SAVE_PATH
from renren.utils.tools import get_function_name

logger = logging.getLogger()

USER_ID_BITS = 'user_id_bits'
redis_helper = RedisHelper(host=REDIS_HOST, port=REDIS_PORT)


class RrUserSpider(scrapy.Spider):
    """
    利用关注被关注关系爬取人人账号
    """
    name = 'rr_user'
    allowed_domains = ['renren.com']
    start_urls = ['http://renren.com/']

    default_headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0(Windows NT6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36',
        'Cache-Control': 'max-age=0',
    }

    default_cookie = {
        'anonymid': 'jty44lbakmt05e',
        'depovince': 'ZJ',
        'jebecookies': '243a96f8-a987-4fbe-978a-48bab9479fc1|||||',
        '_r01_': '1',
        'JSESSIONID': 'abcFqX34R0CxAd8aTjmOw',
        'ick_login': '3d330051-4fec-4666-91f3-b802836c840f',
        't': 'e27b6203b524f49a1c19f9508891b4ea2',
        'societyguester': 'e27b6203b524f49a1c19f9508891b4ea2',
        'id': '970389432',
        'xnsid': 'f06ab2d3',
        'ver': '7.0',
        'loginfrom': 'null',
        'wp_fold': '0',
        'jebe_key': '603bf277-8f92-4b09-b881-123dc6275092|ce72829d7d0b078a68b839ea8c39ea26|1554108655094|1|1554271507674'
    }

    default_visit_id = '970389432'

    def gen_sub_list(self, *, user_id, visit_id, offset):
        """
        :param user_id:  请求用户id
        :param visit_id:  观察者用户id
        :param offset:   10XN
        :return:
        """
        return r'http://follow.renren.com/list/{}/submore?visitId={}&offset={}&limit=10&requestToken=-1887658062&_rtk=5b3d9e0c' \
            .format(user_id, visit_id, offset)

    def gen_pub_list(self, *, user_id, visit_id, offset):
        """
        :param user_id:  请求用户id
        :param visit_id:  观察者用户id
        :param offset:   10XN
        :return:
        """
        return r'http://follow.renren.com/list/{}/pubmore?visitId={}&offset={}&limit=10&requestToken=-1887658062&_rtk=5b3d9e0c' \
            .format(user_id, visit_id, offset)

    def start_requests(self):
        """
        发起初始请求
        :return:
        """

        start_id_list = [
            '859090281',
            '372654328',
            '243098839',
            '427962625',
        ]

        for user_id in start_id_list:
            yield self.request_pub_list(user_id=user_id)
            yield self.request_sub_list(user_id=user_id)

    def request_pub_list(self, *, user_id):
        """
        请求被关注页
        :param user_id:
        :return:
        """
        logger.info('{} pub {}'.format(get_function_name(), user_id))
        # meta = {
        #     'user_id': user_id,
        # }
        pub_list_url = r'http://follow.renren.com/list/{}/pub/v7'.format(user_id)

        return Request(url=pub_list_url, cookies=self.default_cookie, headers=self.default_headers, method='GET',
                       callback=self.parse_pub_total, meta={'user_id': user_id, })

    def request_sub_list(self, *, user_id):
        """
        请求关注页
        :param user_id:
        :return:
        """
        logger.info('{} sub {}'.format(get_function_name(), user_id))
        # meta = {
        #     'user_id': user_id,
        # }
        sub_list_url = r'http://follow.renren.com/list/{}/sub/v7'.format(user_id)

        return Request(url=sub_list_url, cookies=self.default_cookie, headers=self.default_headers, method='GET',
                       callback=self.parse_sub_total, meta={'user_id': user_id, })

    def print_body(self, body):
        soup = BeautifulSoup(body, 'lxml')
        page = soup.prettify()
        print('bs\t', page)

    def parse_pub_total(self, response):
        """
        解析关注者
        :param response:
        :return:
        """
        logger.info("{} Url {}".format(get_function_name(), response.url))

        user_id = response.meta['user_id']

        pub_total = response.xpath("//li[@class='select']/span/text()").extract_first()
        pub_total = int(pub_total)
        offset_total = math.ceil(pub_total / 10.0)

        for i in range(0, offset_total + 1):
            offset = int(i * 10)
            request_url = self.gen_pub_list(user_id=user_id, visit_id=self.default_visit_id, offset=offset)
            yield Request(url=request_url, cookies=self.default_cookie, headers=self.default_headers, method='GET',
                          callback=self.parse_follower_page)

    def parse_sub_total(self, response):
        """
        解析被关注者
        :param response:
        :return:
        """
        logger.info("{} Url {}".format(get_function_name(), response.url))

        user_id = response.meta['user_id']
        pub_total = response.xpath("//li[@class='select']/span/text()").extract_first()
        pub_total = int(pub_total)
        offset_total = math.ceil(pub_total / 10.0)

        for i in range(0, offset_total + 1):
            offset = int(i * 10)
            request_url = self.gen_sub_list(user_id=user_id, visit_id=self.default_visit_id, offset=offset)
            yield Request(url=request_url, cookies=self.default_cookie, headers=self.default_headers, method='GET',
                          callback=self.parse_follower_page)

    def parse_follower_page(self, response):
        """
        解析返回json关注
        :param response:
        :return:
        """
        logger.info("{} Url {}".format(get_function_name(), response.url))
        try:
            datas = json.loads(response.body)
            if 'publisherCount' in datas['data']:
                logger.info("# 1 current process publish list")
            elif 'subscriberCount' in datas['data']:
                logger.info("# 2current process subscribe list")
            else:
                logger.error("#3 unexpected response type")

            users = datas['data']['userList']
            # name_list = []
            for user in users:
                user_id = user['id']
                user_name = user['name']

                # redis 用户id去重
                if redis_helper.bitmap_contains(key=USER_ID_BITS, offset=int(user_id)):
                    logger.info("exists user_id ", user_id)
                    continue
                redis_helper.bitmap_set(key=USER_ID_BITS, offset=int(user_id))

                # 写id到文件
                self.user_id_list_cache.append(str(user_id))
                if len(self.user_id_list_cache) > self.cache_size:
                    file_name = self.gen_file_name()
                    with open(file_name, 'a+') as f:
                        f.write("\r\n".join(self.user_id_list_cache))
                        f.write("\r\n")
                        self.user_id_list_cache.clear()

                # 继续请求用户id
                # yield self.request_pub_list(user_id=user_id)

                # yield self.request_sub_list(user_id=user_id)

                # meta = {
                #     'user_id': user_id,
                # }
                sub_list_url = r'http://follow.renren.com/list/{}/sub/v7'.format(user_id)

                yield Request(url=sub_list_url, cookies=self.default_cookie, headers=self.default_headers,
                              method='GET',
                              callback=self.parse_sub_total, meta={'user_id': user_id, })

                pub_list_url = r'http://follow.renren.com/list/{}/pub/v7'.format(user_id)

                yield Request(url=pub_list_url, cookies=self.default_cookie, headers=self.default_headers,
                              method='GET',
                              callback=self.parse_pub_total, meta={'user_id': user_id, })

                # name_list.append(user_name)
            # print('get new pub new: ', name_list)

            # if len(name_list) == 0:
            #     return
        except Exception as e:
            logger.error("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))
            logger.error("traceback {}".format(traceback.print_exc()))

    # 用户id缓存
    user_id_list_cache = []
    cache_size = 100

    def gen_file_name(self):
        time_str = time.strftime("%Y%m%d%H")
        file_path = SAVE_PATH + "\\id" + "\\id_{}_{}.txt".format(HOST_NAME, time_str)
        return file_path


def run():
    process = CrawlerProcess()
    s = "JOBDIR={}".format(SAVE_PATH + "\\request")
    process.crawl(RrUserSpider)
    process.start()


if __name__ == '__main__':
    run()
