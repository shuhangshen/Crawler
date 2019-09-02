# -*- coding: utf-8 -*-
import json
import logging
import re
import traceback

import os
import scrapy
import time

from scrapy import Request
from scrapy.crawler import CrawlerProcess

from renren.items import RenrenStatusItem
from renren.utils.tools import print_html_body, get_function_name
from renren.utils.setting import SAVE_PATH, ID_PATH

logger = logging.getLogger()


class RrStatusSpider(scrapy.Spider):
    """
    爬取人人状态
    """
    name = 'rr_status'
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
    pt_html_tag = re.compile(r'<[\s\S]+?>')

    MAX_PAGE_SIZE = 1000

    def start_requests(self):

        root_dir = ID_PATH + "\\id\\part1001"
        list_in_path = os.listdir(root_dir)
        list_out_path = []
        # 获取文件夹下所有txt路径
        for i in list_in_path:
            if i == 'id_DL20_2019041119.txt':
                continue
            path = os.path.join(root_dir, i)
            if path.endswith(".txt") and os.path.isfile(path):
                list_out_path.append(path)

        # 逐个txt解析，对每个id 发起请求
        for id_list in list_out_path:
            # id_list = ID_PATH + "\\id\\part1001\\" + "id_DL20_2019041119.txt"
            with open(id_list, "r") as f:
                for line in f:
                    user_id = line.rstrip("\r\n")
                    if len(user_id) == 0:
                        continue
                    # user_id = '505260883'
                    # user_id = '736289665'
                    page = 1
                    # for page in range(1, 100):
                    request_url = r'http://status.renren.com/GetSomeomeDoingList.do?userId={}' \
                                  r'&curpage={}&_jcb=jQuery111108476907948285053_1555050827422' \
                                  r'&requestToken=-1639220190&_rtk=6a0c7a7c&_=1555050827426'.format(user_id, page)
                    yield Request(url=request_url, cookies=self.default_cookie, headers=self.default_headers,
                                  method='GET',
                                  callback=self.parse_req, meta={'user_id': user_id, 'page': str(page)})

    def parse_req(self, response):
        logger.info("{} Url {}".format(get_function_name(), response.url))

        try:
            user_id = response.meta['user_id']
            page = response.meta['page']

            # 从body中提取有效json
            body = response.body
            body = body.decode('utf-8')

            beg = body.find("(")
            body = body[beg + 1:-1]

            dat = json.loads(body)
            doing_array = dat['doingArray']
            contents = ""

            # 解析状态
            for doing in doing_array:
                cont = doing['content']
                cont = re.sub(self.pt_html_tag, " ", cont)
                print(contents)
                cont += "\r\n"
                contents += cont

            if len(contents) == 0:
                logger.info("# END  USER_ID:    {}  ,PAGE:  {}".format(user_id, page))
                return

            # 保存状态
            item = RenrenStatusItem()
            item['url'] = response.url
            item['field'] = time.strftime("%Y%m%d%H")
            item['title'] = user_id + "_" + page
            item['content'] = contents
            logger.info("item :     ", item)
            yield item

            # 本页状态解析成功，则发起下一页的请求
            if int(page) < self.MAX_PAGE_SIZE:
                request_url = r'http://status.renren.com/GetSomeomeDoingList.do?userId={}' \
                              r'&curpage={}&_jcb=jQuery111108476907948285053_1555050827422' \
                              r'&requestToken=-1639220190&_rtk=6a0c7a7c&_=1555050827426'.format(user_id, int(page) + 1)
                yield Request(url=request_url, cookies=self.default_cookie, headers=self.default_headers, method='GET',
                              callback=self.parse_req, meta={'user_id': user_id, 'page': str(int(page) + 1)})
        except Exception as e:
            traceback.print_exc()
            print("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))
            logger.error("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))

    # def parse(self, response):
    #     pass


def run():
    process = CrawlerProcess()
    process.crawl(RrStatusSpider)
    process.start()


if __name__ == '__main__':
    run()
