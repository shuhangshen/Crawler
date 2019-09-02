# -*- coding: utf-8 -*-
import os
import scrapy
from scrapy import Request
from scrapy.crawler import CrawlerProcess
from selenium import webdriver

from toutiao.utils.tools import print_html_body


class TtSimpleSpider(scrapy.Spider):
    name = 'tt_simple'
    allowed_domains = ['toutiao.com']
    start_urls = ['https://landing.toutiao.com/',
                  'https://landing.toutiao.com/ch/news_hot/',
                  'https://landing.toutiao.com/ch/news_tech/',
                  'https://landing.toutiao.com/ch/news_entertainment/',
                  'https://landing.toutiao.com/ch/news_game/',
                  'https://landing.toutiao.com/ch/news_sports/']

    default_header = {
        'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        "Accept-Language": 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Host': 'landing.toutiao.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; W…) Gecko/20100101 Firefox/66.0',
    }

    def start_requests(self):
        for start_url in self.start_urls:
            yield Request(
                url=start_url,

            )
        pass

    def parse_list(self,response):
        print_html_body(response.body)
        pass


def run():
    process = CrawlerProcess()
    process.crawl(TtSimpleSpider)
    process.start()


if __name__ == '__main__':
    run()
    # os.system('scrapy crawl ins_simple')
