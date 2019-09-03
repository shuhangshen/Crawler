# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import json
import logging
import re
from bs4 import BeautifulSoup
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from Guokr.items import GuokrItem
from Guokr.try_except import try_except

logger = logging.getLogger()


class GuokrSpider(scrapy.Spider):
    name = 'guokr'
    allowed_domains = ['guokr.com']
    # start_urls = ['http://guokr.com/']

    fields = {
        'science',
        'calendar',
        'institute',
        'beauty',
    }

    match_word = re.compile(r'[^?/":*<>|]+')
    pattern = re.compile(r'\s|\n|<.*?>', re.S)

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        "Accept-Language": 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Host': 'www.guokr.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; W…) Gecko/20100101 Firefox/66.0',
    }

    def __init__(self):
        print('Enter Init ------')
        super(GuokrSpider, self).__init__()
        self.num = 0
        self.num1 = 0
        self.num2 = 0
        self.num3 = 0

    def start_requests(self):
        #分版块解析页面
        for field in self.fields:
            if field == 'science':
                for i in range(1, 1001):
                    self.num += 1
                    url = 'https://www.guokr.com/beta/proxy/science_api/articles?retrieve_type=by_category&page={}'.format(self.num)
                    try:
                        yield Request(url=url, headers=self.default_headers, meta={'keyword': field}, callback=self.parse_id)
                    except Exception as e:
                        logger.error("parse Request {} failed, reason {}".format(url, e))
            elif field == 'calendar':
                for i in range(1, 363):
                    self.num1 += 1
                    url = 'https://www.guokr.com/apis/minisite/article.json?retrieve_type=by_wx&channel_key=pac&offset={}&limit=10'.format(self.num1*10)
                    try:
                        yield Request(url=url, headers=self.default_headers, meta={'keyword': field}, callback=self.parse_id)
                    except Exception as e:
                        logger.error("parse Request {} failed, reason {}".format(url, e))
            elif field == 'institute':
                #206
                for i in range(1, 206):
                    self.num2 += 1
                    url = 'https://www.guokr.com/apis/minisite/article.json?retrieve_type=by_wx&channel_key=predator&offset={}&limit=10'.format(self.num2*10)
                    try:
                        yield Request(url=url, headers=self.default_headers, meta={'keyword': field}, callback=self.parse_id)
                    except Exception as e:
                        logger.error("parse Request {} failed, reason {}".format(url, e))
            elif field == 'beauty':
                #78
                for i in range(1, 78):
                    self.num3 += 1
                    url = 'https://www.guokr.com/apis/minisite/article.json?retrieve_type=by_wx&channel_key=beauty&offset={}&limit=10'.format(self.num3*10)
                    try:
                        yield Request(url=url, headers=self.default_headers, meta={'keyword': field}, callback=self.parse_id)
                    except Exception as e:
                        logger.error("parse Request {} failed, reason {}".format(url, e))

    #解析页面，通过json格式获取id
    def parse_id(self, response):
        data = json.loads(response.text)
        # print(data)
        field = response.meta['keyword']
        for i in range(0, 10):
            if field == 'science':
                numid = data[i]['id']
                # print(numid)
                url = 'https://guokr.com/article/{}/'.format(numid)
                try:
                    yield Request(url=url, headers=self.default_headers, meta={'keyword': '科学人'}, callback=self.parse_other)
                except Exception as e:
                    logger.error("parse Request {} failed, reason {}".format(url, e))
            elif field == 'calendar':
                numid = data['result'][i]['id']
                # print(numid)
                url = 'https://guokr.com/article/{}/'.format(numid)
                try:
                    yield Request(url=url, headers=self.default_headers, meta={'keyword': '物种日历'}, callback=self.parse_other)
                except Exception as e:
                    logger.error("parse Request {} failed, reason {}".format(url, e))
            elif field == 'institute':
                numid = data['result'][i]['id']
                # print(numid)
                url = 'https://guokr.com/article/{}/'.format(numid)
                try:
                    yield Request(url=url, headers=self.default_headers,
                                  meta={'keyword': '吃货研究所'}, callback=self.parse_other)
                except Exception as e:
                    logger.error("parse Request {} failed, reason {}".format(url, e))
            elif field == 'beauty':
                numid = data['result'][i]['id']
                # print(numid)
                url = 'https://guokr.com/article/{}/'.format(numid)
                try:
                    yield Request(url=url, headers=self.default_headers,
                                  meta={'keyword': '美丽也是种技术'}, callback=self.parse_other)
                except Exception as e:
                    logger.error("parse Request {} failed, reason {}".format(url, e))

    @try_except
    def parse_other(self, response):
        name = response.meta['keyword']
        print("***Start parse article %s***" % response.url)
        item = GuokrItem()

        titlec = response.xpath('//head/title/text()').extract_first()
        titlef = titlec.split('|')[0]
        title = re.findall(self.match_word, titlef)[0].strip()
        print("****标题为:{}***".format(title))
        titlefield = response.xpath(
            '//div[@class="Article__FixedSideTool-sc-1dunux7-1 fXsqHT"]/ul/li[1]/a/text()').extract_first()
        print("***领域为:{}".format(titlefield))
        titlefields = response.xpath(
            '//div[@class="Article__FixedSideTool-sc-1dunux7-1 fXsqHT"]/ul/li[2]/a/text()').extract_first()

        floor_list = response.xpath(
            '//div[@class="layout__Skeleton-zgzfsa-3 styled__ArticleContent-sc-1ctyfcr-4 icatwn"]')
        content = []
        #提取floor_list每一级目录下的文字
        for floor in floor_list:
            content_list = floor.xpath('string(.)').extract_first()
            # print(content_list)
            for i in content_list.split('\r\n'):
                if i != '':
                    content.append(i)
        # print('\r\n'.join(content))
        if len(title) == 0 or len(titlefield) == 0:
            print('此链接未解析出标题或内容: %s' % response.url)
        elif len(content) == 0:
            print('***未解析出内容***')
            return
        elif titlefields is None:
            item['url'] = response.url
            item['title'] = title
            item['field'] = titlefield
            item['fields'] = name
            item['content'] = content
            yield item
        else:
            item['url'] = response.url
            item['title'] = title
            item['field'] = titlefield
            item['fields'] = titlefields
            item['content'] = content
            yield item
