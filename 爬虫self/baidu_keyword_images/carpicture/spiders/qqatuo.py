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
from carpicture.items import QqautoItem
from carpicture.try_except import try_except
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from scrapy.crawler import CrawlerProcess

logger = logging.getLogger()


class QqatuoSpider(scrapy.Spider):
    name = 'qqatuo'
    allowed_domains = ['auto.qq.com']
    start_urls = ['https://auto.qq.com/']
    # start_urls = ['https://data.auto.qq.com/car_public/1/disp_pic_nl.shtml#sid=1579&tid=39&pid=2872101']

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; W…) Gecko/20100101 Firefox/66.0',
    }

    match_num = re.compile(r'\d+')
    match_url = re.compile(r'http://(.*)')
    '''
    def __init__(self):
        print('Enter init------')
        super(QqatuoSpider, self).__init__()
        self.options = webdriver.ChromeOptions()
        self.bro = webdriver.Chrome(chrome_options=self.options)

    def __del__(self):
        print("exit ")
        self.bro.quit()
    '''
    def parse(self, response):
        print("***解析url***")
        links = response.xpath('//dd[@class="carlist"]/ul/li/a/@href').extract()
        titles = response.xpath('//dd[@class="carlist"]/ul/li/a/text()').extract()
        for i in range(0, len(titles)):
            link = 'https://' + re.findall(self.match_url, links[i])[0]
            # print(link)
            yield Request(url=link, meta={'title': titles[i]}, headers=self.default_headers,
                          callback=self.start_requests_car)
            time.sleep(int(random.uniform(1, 2)))

    @try_except
    def start_requests_car(self, response):
        i = 0
        link_list = []
        item = QqautoItem()
        # item = CarpictureItem()
        print('***解析领域***')
        title = response.meta['title']
        print(title)
        cars_url = response.xpath('//div[@class="picsTotal"]/ul/li[2]/a/@href').extract_first()
        # print(cars_url)
        car_url = 'https://' + re.findall(self.match_url, cars_url)[0]
        print(car_url)
        num = response.xpath('//div[@class="picsTotal"]/ul/li[2]/a/text()').extract_first()
        print(num)
        page_num = re.findall(self.match_num, num)[0]
        # totalpage = int(int(page_num) / 12) + 1
        bro = webdriver.Chrome()
        wait = WebDriverWait(bro, 60)
        bro.get(car_url)
        #等待页面刷新
        time.sleep(10)
        #总过有page_num张图片，所以需要循环点击page_num次
        while i <= int(page_num):
            i += 1
            #下面的语句爬到的是缩略图的链接
            # wait.until(EC.presence_of_element_located((By.ID, 'Smailllist')))
            # btn_next_page = bro.find_element_by_id('goright')
            # links = resp.xpath('//li/span/a/img/@src')
            #爬取非缩略图的url
            link_id = wait.until(EC.presence_of_element_located((By.ID, 'download')))
            btn_next_page = bro.find_element_by_id('mouseOverright')
            link = link_id.get_attribute('href')
            print('**link is %s**' % link)
            print("***解析图片链接***")
            #这里爬取的链接为只有一个，是字符串形式，在用imagepipeline类下载图片时，需要以列表形式返回给item,
            if len(link) == 0:
                print("***未解析到URL***")
            else:
                link_list.append(link)
                item['image_urls'] = link_list
                item['url'] = car_url
                item['title'] = title
                item['name'] = 'qqauto'
                yield item
            #moseOverright无法直接点击
            # btn_next_page.click()
            #使用如下方法之一可以点击
            # ActionChains(bro).move_to_element(btn_next_page).click(btn_next_page).perform()
            bro.execute_script("arguments[0].click()", btn_next_page)
            time.sleep(2)


def run():
    process = CrawlerProcess()
    process.crawl(QqatuoSpider)
    process.start()


if __name__ == '__main__':
    run()
    # os.system('scrapy crawl qqatuo')

