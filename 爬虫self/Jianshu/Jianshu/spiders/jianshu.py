# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import logging
import time
import re
from lxml import etree
from Jianshu.items import JianshuItem
from Jianshu.utils.try_except import try_except
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from scrapy.crawler import CrawlerProcess

logger = logging.getLogger()

class JianshuSpider(scrapy.Spider):
    name = 'jianshu'
    allowed_domains = ['jianshu.com']
    # start_urls = ['https://www.jianshu.com/']

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        "Accept-Language": 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Host': 'www.jianshu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; W…) Gecko/20100101 Firefox/66.0',
    }

    match_char = re.compile(r'[?/":*<>|]+')

    def __init__(self):
        print('Enter Init ------')
        super(JianshuSpider, self).__init__()

    def __del__(self):
        print("exit ")

    def start_requests(self):
        print("***开始分页解析推荐作者栏目***")
        #101
        for i in range(1, 101):
            url = 'https://www.jianshu.com/recommendations/users?page={}'.format(i)
            try:
                yield Request(url=url, headers=self.default_headers, callback=self.parse_author)
            except Exception as e:
                logger.error('{} response failed, Reason:{}'.format(url, e))

    def parse_author(self, response):
        print("****解析推荐作者页面链接****")
        author_ids = response.xpath('//div[@class="row"]/div[@class="col-xs-8"]/div/a/@href').extract()
        for author in author_ids:
            author_id = re.sub(r'users', 'u', author)
            url = 'https://www.jianshu.com' + author_id
            # print(url)
            options = webdriver.ChromeOptions()
            # 无界面
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            bro = webdriver.Chrome(chrome_options=options)
            wait = WebDriverWait(bro, 60)
            bro.get(url)
            time.sleep(5)
            # 懒加载将页面滚动条拖到底部
            check_height = bro.execute_script("return document.body.scrollHeight;")
            while True:
                bro.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                try:
                    wait.until(
                        lambda driver: bro.execute_script("return document.body.scrollHeight;") > check_height)
                    check_height = bro.execute_script("return document.body.scrollHeight;")
                except TimeoutException:
                    break
            time.sleep(3)
            resp = etree.HTML(bro.page_source)
            author = resp.xpath('//div[@class="main-top"]/div/a/text()')[0]
            print("解析作者:{},链接为:{}".format(author, url))
            links = resp.xpath('//div[@class="content "]/a/@href')
            wait.until(EC.presence_of_element_located((By.ID, 'list-container')))
            for link in links:
                url = 'https://www.jianshu.com' + link
                # print("***{}***".format(url))
                try:
                    yield Request(url=url, headers=self.default_headers, meta={'name': author}, callback=self.parse)
                except Exception as e:
                    logger.error('{} response fail, Reason: {}'.format(url, e))

    def parse(self, response):
        print("***开始解析文章***")
        item = JianshuItem()
        author = response.meta['name']
        titlec = response.xpath('//head/title/text()').extract_first()
        title = re.sub(self.match_char, '-', titlec).split()[0]
        print("解析文章: %s" % title)
        floor_list = response.xpath('//div[@class="show-content-free"]')
        content = []
        # 提取floor_list每一级目录下的文字
        for floor in floor_list:
            content_list = floor.xpath('string(.)').extract_first()
            # print(content_list)
            for i in content_list.split('\n'):
                if i != '':
                    content.append(i)

        if len(author) == 0 or len(title) == 0:
            print("此链接:%s未解析出文章" % response.url)
        elif content is None:
            logger.error('付费文章，不读取')
            return
        else:
            item['url'] = response.url
            item['author'] = author
            item['title'] = title
            item['content'] = content
            yield item


def run():
    process = CrawlerProcess()
    process.crawl(JianshuSpider)
    process.start()


if __name__ == '__main__':
    run()
    # os.system('scrapy crawl jianshu')






