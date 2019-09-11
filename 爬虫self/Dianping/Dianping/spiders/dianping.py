# -*- coding: utf-8 -*-
import scrapy
import re
import copy
import time
import random

from scrapy import Request
from fake_useragent import UserAgent
from Dianping.items import DianpingItem


class DianpingSpider(scrapy.Spider):
    name = 'dianping'
    allowed_domains = ['dianping.com']
    start_urls = ['https://www.dianping.com/hangzhou/']
    # start_urls = ['http://www.dianping.com/shop/92767588/review_all']

    match_char = re.compile(r'[?/":*<>|]+')
    match_word = re.compile(r'[^\t ]+')
    #贪婪匹配
    match_page = re.compile(r'/p(.*)')

    User_Agent = UserAgent()

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        "Accept-Language": 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Host': 'www.dianping.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    default_cookies = {'cy': '3', 'cye': 'hangzhou', '_lxsdk_cuid': '16cd6170c194b-0a828e530eaec-3c375f0d-1fa400-16cd6170c1ac8',
                       '_lxsdk': '16cd6170c194b-0a828e530eaec-3c375f0d-1fa400-16cd6170c1ac8',
                       '_hc.v': '96148712-7cc1-2d7d-446a-066359121f20.1566959931', '_dp.ac.v': '7a9dbc50-70d7-4f3d-89f8-40cc86693884',
                       'dper': 'd64d4c0bc7d6ead79e8da49e39a4dc1f8585178d88744f2cf5a484cf097ba794f5182892dbf13e1e4a9f16a6ad3efa8f6eb921906187cbec5f04185a98329e6eee77fad3f53414fe1063e16f00b3c42376c051fc5142b80d832af0df88ce28b1',
                       'll': '7fd06e815b796be3df069dec7836c3df', 'ua': 'dpuser_1704722097', 'ctu': '588c62d8e9c5082144d402a73852c1ce19415749938960e6aebae86be0314f6d',
                       'uamo': '13588829630', 's_ViewType': '10', '_lx_utm': 'utm_source%3DBaidu%26utm_medium%3Dorganic'
                       }

    def __init__(self):
        print('Enter Init ------')
        super(DianpingSpider, self).__init__()

    def __del__(self):
        print("Exit ------")

    def start_requests(self):
        headers = copy.deepcopy(self.default_headers)
        headers['User_Agent'] = self.User_Agent.random
        # url = "http://www.dianping.com/shop/92767588/review_all/p1"
        url = "http://www.dianping.com/shop/124327928/review_all/p1"
        # yield Request(url=url, cookies=self.default_cookies, headers=self.default_headers, callback=self.parse, dont_filter=True)
        yield Request(url=url,  headers=self.default_headers, cookies=self.default_cookies, callback=self.parse, dont_filter=True)

    def parse(self, response):
        item = DianpingItem()
        shop = response.xpath('//div[@class="review-shop-wrap"]/div/h1/text()').extract_first()
        floor_list = response.xpath('//div[@class="main-review"]')
        # 提取floor_list每一级目录下的文字
        for floor in floor_list:
            content = []
            content_list = floor.xpath('string(.)').extract_first()
            # print(content_list)
            for i in content_list.split():
                if i != '':
                    content.append(i)
            users = re.sub(self.match_char, '', content[0])
            item['users'] = users
            item['url'] = response.url
            item['shop'] = shop
            item['content'] = content
            yield item


        # 循环翻页
        page = response.xpath('//div[@class="reviews-pages"]/a/text()').extract()
        next_page = page[-1]

        if next_page == '下一页':
            headers = copy.deepcopy(self.default_headers)
            headers['User_Agent'] = self.User_Agent.random
            num = re.findall(self.match_page, response.url)[0]
            print("Request Url: {}".format(response.url))
            # print(num)
            page_num = int(num) + 1
            url = re.sub(self.match_page, '/p' + str(page_num), response.url)
            time.sleep(int(random.uniform(2, 5)))
            yield Request(url=url, cookies=self.default_cookies, headers=self.default_headers, callback=self.parse)
            # yield Request(url=url,  headers=headers, callback=self.parse)
