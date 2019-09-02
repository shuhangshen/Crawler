# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import logging
import time
import re

from Jianshu.items import JianshuItem
from Jianshu.utils.try_except import try_except
from scrapy.crawler import CrawlerProcess

logger = logging.getLogger()


class Jianshu1Spider(scrapy.Spider):
    name = 'jianshu1'
    allowed_domains = ['jianshu.com']
    # start_urls = ['https://jianshu.com/']

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        "Accept-Language": 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        # 'Host': 'www.jianshu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; W…) Gecko/20100101 Firefox/66.0',
    }

    match_char = re.compile(r'[?/":*<>|]+')
    match_num = re.compile(r'page=(\d+)')

    def __init__(self):
        print('Enter Init ------')
        super(Jianshu1Spider, self).__init__()

    def __del__(self):
        print("exit ")

    def start_requests(self):
        #101
        for i in range(1, 17):
            print("***开始分页解析推荐作者栏目,页面:{}***".format(i))
            url = 'https://www.jianshu.com/recommendations/users?page={}'.format(i)
            try:
                yield Request(url=url, headers=self.default_headers, callback=self.parse_author)
            except Exception as e:
                logger.error('{} response failed, Reason:{}'.format(url, e))

    def parse_author(self, response):
        author_ids = response.xpath('//div[@class="row"]/div[@class="col-xs-8"]/div/a/@href').extract()
        for author in author_ids:
            author_id = re.sub(r'users', 'u', author)
            url = 'https://www.jianshu.com' + author_id + '?order_by=shared_at&page=1'
            print("****解析推荐作者页面链接:{}****".format(url))
            try:
                yield Request(url=url, headers=self.default_headers,
                              meta={'author_id': author_id}, callback=self.parse_page)
            except Exception as e:
                logger.error('{} response failed, Reason:{}'.format(url, e))

    def parse_page(self, response):
        author_id = response.meta['author_id']
        author = response.xpath('//div[@class="main-top"]/div/a/text()').extract_first()
        article_nums = response.xpath('//div[@class="info"]/ul/li[3]/div/a/p/text()').extract_first()
        links = response.xpath('//div[@class="content "]/a/@href').extract()
        for link in links:
            url = 'https://www.jianshu.com' + link
            # print("***{}***".format(url))
            try:
                yield Request(url=url, headers=self.default_headers, meta={'name': author}, callback=self.parse)
            except Exception as e:
                logger.error('{} response fail, Reason: {}'.format(url, e))
        #循环翻页
        num = int(article_nums) // 9
        com = re.findall(self.match_num, response.url)[0]
        if int(com) <= num:
            id_num = int(com) + 1
            url = 'https://www.jianshu.com{}?order_by=shared_at&page={}'.format(author_id, id_num)
            try:
                yield Request(url=url, headers=self.default_headers,
                              meta={'author_id': author_id}, callback=self.parse_page)
            except Exception as e:
                logger.error('{} response fail, Reason: {}'.format(url, e))

    def parse(self, response):
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
    process.crawl(Jianshu1Spider)
    process.start()


if __name__ == '__main__':
    run()
    # os.system('scrapy crawl jianshu1')