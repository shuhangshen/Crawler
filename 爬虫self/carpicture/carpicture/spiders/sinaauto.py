# -*- coding: utf-8 -*-
import scrapy
import re
import random
import os
import logging
import time
import urllib.request
from scrapy import Request
from lxml import etree
from carpicture.items import SinaautoItem
from carpicture.try_except import try_except
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from scrapy.crawler import CrawlerProcess

logger = logging.getLogger()


class SinaautoSpider(scrapy.Spider):
    name = 'sinaauto'
    allowed_domains = ['auto.sina.com.cn']
    start_urls = ['https://auto.sina.com.cn/']

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; W…) Gecko/20100101 Firefox/66.0',
    }

    match_num = re.compile(r'\d+')
    match_url = re.compile(r'http://(.*)')

    def __init__(self):
        print('Enter Init sinaauto ------')
        super(SinaautoSpider, self).__init__()

    def __del__(self):
        print('Exit sinauto------')

    def parse(self, response):
        print('***解析各个汽车类型的URL***')
        links = response.xpath('//div[@class="tab-content"]/ul/li/a/@href').extract()
        titles = response.xpath('//div[@class="tab-content"]/ul/li/a/text()').extract()
        for i in range(0, len(titles)):
            yield Request(url=links[i], headers=self.default_headers, meta={'title': titles[i]},
                          callback=self.start_requests_parse)
            time.sleep(int(random.uniform(5, 10)))

    @try_except
    def start_requests_parse(self, response):
        i = 0
        link_list = []
        item = SinaautoItem()
        # item = CarpictureItem()
        print('***解析领域***')
        title = response.meta['title']
        print(title)
        cars_url = response.xpath('//div[@class="simg"]/a/@href').extract_first()
        car_url = 'https:' + cars_url
        print(car_url)
        bro = webdriver.Chrome()
        wait = WebDriverWait(bro, 60)
        bro.get(car_url)
        # 等待页面刷新
        time.sleep(10)
        resp = etree.HTML(bro.page_source)
        nums = resp.xpath('//span[@class="page"]/em/text()')[0]
        # nums = 35
        numb = resp.xpath('//span[@class="page"]/strong/text()')[0]
        page_num = int(numb) - int(nums)
        # 总共有page_num张图片，所以需要循环点击page_num次
        while i <= int(page_num):
            i += 1
            wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="main_area"]')))
            # link_id = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="main_pic"]/img')))
            link_id = bro.find_element(By.XPATH, '//div[@class="main_pic"]/img')
            btn_next_page = bro.find_element_by_xpath('//div[@class="main_pic"]/a[@class="btn_right"]')
            link = link_id.get_attribute('src')
            # link = 'https://' + re.findall(self.match_url, url)[0]
            print('**link is %s**' % link)
            print("***解析图片链接***")
            # 这里爬取的链接为只有一个，是字符串形式，在用imagepipeline类下载图片时，需要以列表形式返回给item,
            if len(link) == 0:
                print("***未解析到URL***")
            else:
                link_list.append(link)
                item['image_urls'] = link_list
                item['url'] = car_url
                item['title'] = title
                item['name'] = 'sinaauto'
                yield item
            # moseOverright无法直接点击
            # btn_next_page.click()
            # 使用如下方法之一可以点击
            # ActionChains(bro).move_to_element(btn_next_page).click(btn_next_page).perform()
            bro.execute_script("arguments[0].click()", btn_next_page)
            time.sleep(2)


def run():
    process = CrawlerProcess()
    process.crawl(SinaautoSpider)
    process.start()


if __name__ == '__main__':
    run()
    # os.system('scrapy crawl sinaauto')
