# -*- coding: utf-8 -*-
import scrapy
import re
import logging
import os
import random
from lxml import etree
import time
from scrapy import Request
from scrapy.crawler import CrawlerProcess
from XueKeW.items import XuekewItem
from XueKeW.utils.tools import get_function_name

logger = logging.getLogger()


class ZxxkSpider(scrapy.Spider):
    name = 'zxxk'
    allowed_domains = ['zxxk.com']
    # start_urls = ['http://zxxk.com/']
    start_urls = ['http://yw.zxxk.com/articlelist']
    field = {
        'yw',
        'sx',
        'yy',
        'wl',
        'hx',
        'sw',
        'zz',
        'ls',
        'dl',
        'kx',
    }

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        "Accept-Language": 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Host': 'zxxk.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; W…) Gecko/20100101 Firefox/66.0',

    }

    match_page = re.compile(r'\d+')
    match_url = re.compile(r'http://.*?com')
    match_url2 = re.compile(r'http://.*?/class\d+')

    def __init__(self):
        print('Enter Init ------')
        super(ZxxkSpider, self).__init__()

    def __del__(self):
        print('Enter Destory ------')

    def rand_sleep(self, *, rand_value, rand_max, sleep_min, sleep_max):
        if (random.uniform(0, rand_max)) < rand_value:
            print("sleeping .....")
            time.sleep(int(random.uniform(sleep_min, sleep_max)))
        print("continuing .....")

    # 生成指定referer的头
    def generate_headers(self, referer):
        headers = self.default_headers
        headers['Referer'] = referer
        return headers

    def get_num(self, response):
        page = response.xpath('//div[@class="list-page"]/span/text()').extract_first()
        page_num = re.findall(self.match_page, str(page))
        return page_num

    '''
    def parse(self, response):
        headers_url = re.findall(self.match_url2, response.url)
        headers = self.generate_headers(headers_url)
        last_url_links = response.xpath('//div[@class="cont-rt"]//div[@class="clearfix"]/a/@href').extract()
        for last_url_link in last_url_links:
            last_link = re.findall(self.match_url, response.url)[0] + last_url_link
            yield Request(url=last_link, headers=headers, callback=self.parse_xueke)
    '''

    #遍历每个领域的文字版块
    def parse(self, response):
        for field in self.field:
            while True:
                self.rand_sleep(rand_value=10, rand_max=200, sleep_min=2, sleep_max=5)
                if field in ['sw']:
                    url = r'http://{}.zxxk.com/articlelist/'.format(field)
                    headers = self.generate_headers(url)
                    yield Request(url=url, headers=headers, meta={'field': field}, callback=self.start_request_url)
                else:
                    url = r'http://{}.zxxk.com/articlelist/'.format(field)
                    headers_url = r'http://{}.zxxk.com/'.format(field)
                    headers = self.generate_headers(headers_url)
                    yield Request(url=url, headers=headers, meta={'field': field},  callback=self.start_request_url)
                    print('fields {} extrated'.format(field))
                    time.sleep(5)
                    break

    #在各个领域中遍历Url
    def start_request_url(self, response):
        print("start requesting ...")
        time.sleep(1)
        # headers_url = re.findall(self.match_url, response.url)
        # headers = self.generate_headers(response.url)
        links = response.xpath('//ul[@class="det-nav"]//li/a/@href').extract()
        for link in links:
            some_request_url = re.findall(self.match_url, response.url)[0] + link
            headers = self.generate_headers(some_request_url)
            yield Request(url=some_request_url, headers=headers, callback=self.start_request_url2)

    #遍历每个分页
    def start_request_url2(self, response):
        page = response.xpath('//div[@class="list-page"]/span/text()').extract_first()
        page_num = re.findall(self.match_page, str(page))
        if len(page_num) == 0:
            some_request_url = response.url
            headers = self.generate_headers(some_request_url)
            yield Request(url=some_request_url, headers=headers, callback=self.acquire_requests)
        else:
            for num in range(int(page_num[0])+1):
                if num == 0 or num == 1:
                    some_request_url = response.url
                    print('request.....', some_request_url)
                    headers = self.generate_headers(some_request_url)
                    yield Request(url=some_request_url, headers=headers, callback=self.acquire_requests)
                else:
                    some_request_url = response.url + '/index-{}.html'.format(num)
                    print('request.....', some_request_url)
                    headers = self.generate_headers(some_request_url)
                    yield Request(url=some_request_url, headers=headers, callback=self.acquire_requests)

    #开始解析对应具体文字内容的url
    def acquire_requests(self, response):
        print('start request  %s url page' % response.url)
        headers_url = re.findall(self.match_url2, response.url)
        headers = self.generate_headers(headers_url)
        last_url_links = response.xpath('//div[@class="cont-rt"]//div[@class="clearfix"]/a/@href').extract()
        for last_url_link in last_url_links:
            last_link = re.findall(self.match_url, response.url)[0] + last_url_link
            yield Request(url=last_link, headers=headers, callback=self.parse_xueke)

    #解析内容
    def parse_xueke(self, response):
        print("parese article %s" % response.url)
        item = XuekewItem()
        title = response.xpath('//head/title/text()').extract()
        content = response.xpath('//p/text()').extract()
        field = response.xpath('//ul[@class="crumb"]/li/a/text()').extract_first()#注意这里是UL(小写)，不是U1(234)的1
        # print(field)
        fields = response.xpath('//li/span/a/@title').extract()
        # print(fields)
        if len(title) == 0 or len(content) == 0 or len(fields) == 0:
            print("未解析到对应链接标题、内容或领域")
            return
        item['url'] = response.url
        item['title'] = ''.join(title[0].split())
        item['content'] = content
        item['field'] = time.strftime("%Y%m%d") + os.sep + field[2:]
        item['field1'] = fields[1]
        yield item

    '''
    def acquire_requests1(self):
        pass
    '''


def run():
    process = CrawlerProcess()
    process.crawl(ZxxkSpider)
    process.start()


if __name__ == '__main__':
    # run()
    os.system('scrapy crawl zxxk')







