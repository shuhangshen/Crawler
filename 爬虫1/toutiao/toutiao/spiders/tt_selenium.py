# -*- coding: utf-8 -*-
import html
import logging
import random
import re

import os
from lxml import etree

import scrapy
import time

from bs4 import BeautifulSoup
from scrapy import Request
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from toutiao.items import ToutiaoItem
from toutiao.utils.tools import get_function_name, print_html_body
from toutiao.utils.try_except import try_except

logger = logging.getLogger()


class TtSeleniumSpider(scrapy.Spider):
    name = 'tt_selenium'
    allowed_domains = ['toutiao.com']
    # start_urls = ['http://toutiao.com/']

    host = 'https://www.toutiao.com/'

    start_urls = [
        'https://landing.toutiao.com/ch/news_tech/',
    ]

    # 爬取领域
    fields = [
        'news_tech',
        'news_entertainment',
        'news_game',
        'news_sports',
        'news_car',
        'news_finance',
        'news_military',
        'news_world',
        'news_fashion',
        'news_discovery',
        'news_regimen',
        'news_travel',
        'news_essay',
        'news_food',
    ]
    default_header = {
        'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        "Accept-Language": 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Host': 'www.toutiao.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; W…) Gecko/20100101 Firefox/66.0',
    }

    match_id = re.compile(r'\d+')
    match_space = re.compile(r'[\n ]')

    def __init__(self):
        print('Enter Init ------')
        super(TtSeleniumSpider, self).__init__()

        browser_options = webdriver.ChromeOptions()
        # 使用无头浏览器
        # browser_options.add_argument('--headless')
        # browser_options.add_argument('--disable-gpu')

        self.browser = webdriver.Chrome(chrome_options=browser_options)

    def __del__(self):
        print('Enter Destory ------')
        self.browser.quit()

    def rand_sleep(self, *, rand_value, rand_max, sleep_min, sleep_max):
        if (random.uniform(0, rand_max)) < rand_value:
            print("sleeping .....")
            time.sleep(int(random.uniform(sleep_min, sleep_max)))
        print("continuing .....")

    def start_requests(self):
        print("start requesting ...")

        # 1. 遍历所有版块
        for field in self.fields:
            url = r'https://landing.toutiao.com/ch/{}/'.format(field)
            print("requesting ... ", url)
            self.browser.get(url)

            time.sleep(3)
            # 1. 访问版块首页，获取当前的列表
            while True:
                self.rand_sleep(rand_value=10, rand_max=200, sleep_min=2, sleep_max=5)
                ActionChains(self.browser).key_down(Keys.DOWN).perform()
                title_pubs = self.browser.find_elements(By.XPATH,
                                                        "//div[@class='y-left']/span[@class='lbtn']")
                # EXIT :'1天前'
                if len(title_pubs) > 0 and title_pubs[-1].text.strip() == '1天前':
                    resp = etree.HTML(self.browser.page_source)
                    # 2. 提取列表中的文章URL，发送请求
                    links = resp.xpath("//div[@class='title-box']/a[@class='link title']/@href")
                    for link in links:
                        uid = re.findall(self.match_id, link)[0]
                        request_url = self.host + 'a{}'.format(uid)

                        print('requesting ', request_url)
                        yield Request(url=request_url, meta={
                            'field': field
                        }, callback=self.parse_article)
                        # 从循环中退出
                    print('fields {} extracted '.format(field))
                    time.sleep(5)
                    break

    @try_except
    def parse_article(self, response):
        logger.info("{} Url {}".format(get_function_name(), response.url))

        scripts = response.xpath('//script/text()').extract()
        for script in scripts:
            script = script.lstrip()
            # 1. 找到记录数据的script, 提取content字段
            if script.startswith('var BASE_DATA'):
                script.replace("\n", "")
                script = re.sub(self.match_space, "", script)
                start_tag = "content:'"
                start_idx = script.find(start_tag)
                end_idx = script.find("',", start_idx)
                if start_idx != -1 and end_idx != -1:
                    script = script[start_idx + len(start_tag):end_idx]
                    # 2. 获取content转义后提取文本
                    data = html.unescape(script)
                    soup = BeautifulSoup(data, 'lxml')
                    texts = "\r\n".join([p.text for p in soup.select('p')])
                    if len(texts.strip()) == 0:
                        continue
                    # 3. 记录文本
                    item = ToutiaoItem()
                    item['url'] = response.url
                    item['field'] = time.strftime("%Y%m%d") + os.sep + response.meta['field']
                    item['title'] = time.strftime("%Y%m%d_%H%M%S_") + str(random.randint(0, 1000))
                    item['content'] = texts
                    print('dump item:   ', item['url'])
                    yield item


def run():
    process = CrawlerProcess()
    process.crawl(TtSeleniumSpider)
    process.start()


if __name__ == '__main__':
    # run()
    os.system('scrapy crawl tt_selenium')
