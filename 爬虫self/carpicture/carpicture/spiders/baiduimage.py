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
from carpicture.items import BaiduimageItem
from carpicture.try_except import try_except
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from scrapy.crawler import CrawlerProcess


class BaiduimageSpider(scrapy.Spider):
    name = 'baiduimage'
    allowed_domains = ['image.baidu.com']
    start_urls = ['https://image.baidu.com/']
    keywords_file = r'C:\Users\YJY\Desktop\workspace\carpicture\keywords.txt'

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        "Accept-Language": 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Host': 'image.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
    }

    def __init__(self):
        print('Enter Init ------')
        super(BaiduimageSpider, self).__init__()
        self.options = webdriver.ChromeOptions()
        #无界面
        # self.options.add_argument('--headless')
        # self.options.add_argument('--disable-gpu')
        self.bro = webdriver.Chrome(chrome_options=self.options)
        self.wait = WebDriverWait(self.bro, 60)
        self.bro.get('https://image.baidu.com/')
        self.log_file = open(r'C:\Users\YJY\Desktop\workspace\carpicture\log.txt', 'w', encoding='utf-8')
        print("init end")

    def __del__(self):
        print("exit ")
        self.bro.quit()

    #懒加载，页面下滑到底端
    def scroll_until_loaded(self):
        check_height = self.bro.execute_script("return document.body.scrollHeight;")
        while True:
            self.bro.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                self.wait.until(
                    lambda driver: self.bro.execute_script("return document.body.scrollHeight;") > check_height)
                check_height = self.bro.execute_script("return document.body.scrollHeight;")
            except TimeoutException:
                break

    def parse(self, response):
        # 遍历关键词
        for keyword in open(self.keywords_file, 'r', encoding='utf-8'):
            keyword = keyword.strip()
            print('开始搜索关键字:%s' % keyword)
            print('开始搜索关键字:%s' % keyword, file=self.log_file)

            # dd
            resp = etree.HTML(self.bro.page_source)
            key = resp.xpath('//head/meta[2]/@name')
            # print(key)

            # 将关键词输入到搜索框，点击搜索
            try:
                if key:
                    input_search = self.wait.until(EC.presence_of_element_located((By.ID, 'kw')))
                    # btn_search =  self.bro.find_element_by_xpath('//span[@class="s_search"]')
                    btn_search = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//span[@class="s_search"]')))
                    input_search.clear()
                    input_search.send_keys(keyword)
                    btn_search.click()
                    # self.bro.execute_script("arguments[0].click()", btn_search)
                    time.sleep(5)
                    # self.wait.until(EC.presence_of_element_located((By.ID, 'imgid')))
                    # ActionChains(self.bro).key_down(Keys.DOWN).perform()
                    self.scroll_until_loaded()
                    time.sleep(15)
                    # self.wait.until(EC.presence_of_element_located((By.ID, 'imgContainer')))
                else:
                    input_search = self.wait.until(EC.presence_of_element_located((By.ID, 'kw')))
                    btn_search = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, '//span[@class="s_btn_wr"]/input[@class="s_btn"]')))
                    input_search.clear()
                    input_search.send_keys(keyword)
                    btn_search.click()
                    time.sleep(5)
                    self.wait.until(EC.presence_of_element_located((By.ID, 'imgid')))
                    # ActionChains(self.bro).key_down(Keys.DOWN).perform()
                    self.scroll_until_loaded()
                    time.sleep(5)
            except Exception as reason:
                print('搜索关键词%s出错%s' % (keyword, reason), file=self.log_file)
                self.bro.refresh()
                continue
            content = etree.HTML(self.bro.page_source)
            links = content.xpath('//li[@class="imgitem"]/@data-objurl')
            item = BaiduimageItem()
            item['image_urls'] = links
            item['title'] = keyword
            item['name'] = 'baiduimage'
            yield item


def run():
    process = CrawlerProcess()
    process.crawl(BaiduimageSpider)
    process.start()


if __name__ == '__main__':
    run()
    # os.system('scrapy crawl baiduimage')
