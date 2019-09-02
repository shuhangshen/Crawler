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
from carpicture.items import AutohomeItem
from carpicture.try_except import try_except
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from scrapy.crawler import CrawlerProcess

logger = logging.getLogger()


class AutohomeSpider(scrapy.Spider):
    name = 'autohome'
    allowed_domains = ['autohome.com.cn/hangzhou']
    start_urls = ['https://www.autohome.com.cn/hangzhou/']

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    }

    match_num = re.compile(r'\d+')
    match_url = re.compile(r'http://(.*)')

    def __init__(self):
        print('Enter Init autohome ------')
        super(AutohomeSpider, self).__init__()

    def __del__(self):
        print('Exit autohome------')

    def parse(self, response):
        print('***解析各个汽车类型的URL***')
        links = response.xpath('//div[@class="box"]/p[1]/a/@href').extract()
        # print(links)
        titles = response.xpath('//div[@class="box"]/p[1]/a/text()').extract()
        print(titles)
        for i in range(0, len(titles)):
            try:
                yield Request(url='https://www.autohome.com.cn' + links[i], headers=self.default_headers,
                              meta={'title': titles[i]}, callback=self.start_requests_parse, dont_filter=True)
            except Exception as e:
                logger.error("parser Request {} faild, reason:{}".format('https://www.autohome.com.cn' + links[i], e))
            time.sleep(int(random.uniform(5, 10)))

    @try_except
    def start_requests_parse(self, response):
        try:
            i = 0
            link_list = []
            item = AutohomeItem()
            # item = CarpictureItem()
            print('***解析领域***')
            title = response.meta['title']
            print(title)
            cars_url = response.xpath('//ul[@class="pic-list"]/li[4]/a/@href').extract_first()
            car_url = 'https:' + cars_url
            print(car_url)
            # 这里由于下面的悬浮操作，会出现not implemented,所以加个options
            options = webdriver.ChromeOptions()
            options.add_argument('--log-level=3')
            bro = webdriver.Chrome(executable_path=r'C:\Users\YJY\AppData\Local\Google\Chrome\Application\chromedriver.exe',
                                   chrome_options=options)
            wait = WebDriverWait(bro, 60)
            bro.get(car_url)
            # 等待页面刷新
            time.sleep(10)
            btn = bro.find_element_by_xpath('//div[@class="type-show"]/ul/li[3]/a')
            bro.execute_script("arguments[0].click()", btn)
            time.sleep(2)
            resp = etree.HTML(bro.page_source)
            #获取图片数量
            nums = resp.xpath('//div[@class="type-show"]/ul/li[3]/a/span/text()')[0]
            page_num = re.findall(self.match_num, nums)[0]
            # 总共有page_num张图片，所以需要循环点击page_num次
            while i <= int(page_num):
                i += 1
                wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="pic"]')))
                # link_id = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="main_pic"]/img')))
                link_id = bro.find_element(By.ID, 'img')
                #这里需要鼠标悬浮，使节点出现
                btn_onside = bro.find_element_by_id('img')
                ActionChains(bro).move_to_element(btn_onside).perform()
                time.sleep(3)
                btn_next_page = bro.find_element_by_xpath('//div[@class="pic"]/img[@onside="1"]')
                link = link_id.get_attribute('src')
                # link = 'https://' + re.findall(self.match_url, url)[0]
                print('**link is %s**' % link)
                print("***解析图片链接***")
                # 这里爬取的链接只有一个，是字符串形式，在用imagepipeline类下载图片时，需要以列表形式返回给item,
                if len(link) == 0:
                    print("***未解析到URL***")
                else:
                    link_list.append(link)
                    item['image_urls'] = link_list
                    item['url'] = car_url
                    item['title'] = title
                    item['name'] = 'autohome'
                    yield item
                bro.execute_script("arguments[0].click()", btn_next_page)
                time.sleep(2)
        finally:
            bro.close()


def run():
    process = CrawlerProcess()
    process.crawl(AutohomeSpider)
    process.start()


if __name__ == '__main__':
    run()
    # os.system('scrapy crawl autohome')
