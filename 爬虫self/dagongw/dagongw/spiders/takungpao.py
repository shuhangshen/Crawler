# -*- coding: utf-8 -*-
import scrapy
import re
import logging
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from dagongw.items import DagongwItem
import time
import os
logger = logging.getLogger()

class TakungpaoSpider(CrawlSpider):
    name = 'takungpao'
    allowed_domains = ['takungpao.com']
    # start_urls = ['http://takungpao.com/']
    deny_domains = ['auto.takungpao.com''photo.takungpao.com', 'comments.takungpao.com', 'ent.takungpao.com', 'news.takungpao.com', 'arts.takungpao.com']
    start_urls = ['http://www.takungpao.com/']

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//u1[@class="nav_list clearfix"]', deny_domains=deny_domains),
             process_links='url_acquire', follow=True),
        Rule(LinkExtractor(restrict_xpaths='//div[@class="list card show"]', deny_domains=deny_domains),
             process_links='link_parse', follow=True),
        Rule(LinkExtractor(restrict_xpaths='//div[@class="chanye_wrap"]', deny_domains=deny_domains),
             process_links='url_acquire', follow=True),
        Rule(LinkExtractor(allow=r'.*?www.takungpao.com/culture.*?'), callback='parse_article', follow=True),
        Rule(LinkExtractor(allow=r'.*?www.takungpao.com/news.*?'), callback='parse_article', follow=True),
        Rule(LinkExtractor(allow=r'.*?www.takungpao.com/lens.*?'), callback='parse_article', follow=True),
        Rule(LinkExtractor(allow=r'.*?www.takungpao.com/opinion.*?'), callback='parse_article', follow=True),
        Rule(LinkExtractor(allow=r'.*?www.takungpao.com/life.*?'), callback='parse_article', follow=True),
        Rule(LinkExtractor(allow=r'.*?www.takungpao.com/special.*?'), callback='parse_article', follow=True),
        Rule(LinkExtractor(allow=r'.*?renwen.takungpao.com/.*?'), callback='parse_article1', follow=True),
        Rule(LinkExtractor(allow=r'.*?sports.takungpao.com/.*?'), callback='parse_article1', follow=True),
        Rule(LinkExtractor(allow=r'.*?www.takungpao.com/.*?', deny_domains=deny_domains), callback='parse_article', follow=True),
        Rule(LinkExtractor(allow=r'.*?takungpao.com/.*?', deny_domains=deny_domains), callback='parse_article1', follow=True),
    )

    #判断是否是url链接
    def is_url(self, url):
        pat = r'(((http|ftp|https)://)(([a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))\
              (:[0-9]{1,4})*(/[a-zA-Z0-9\&%_\./-~-]*)?)'#网址正则表达式
        re_url = re.compile(pat)
        result = re.search(re_url, url)
        return result

    def link_parse(self, links):
        print('****** Get %d links******' % len(links))
        return links

    def url_acquire(self, response):
        url = response.xpath('//div[@class="tpk_page"]/a/@href')
        if self.is_url(url):
            return url
        else:
            links = 'http://www.takungpao.com/' + url
            return links


    def parse_article(self, response):
        print('Enter parse_article')
        item = DagongwItem()
        title = response.xpath('//head/title/text()').extract() #修改去掉汉子中的特殊符号*\、等，下同
        texts = response.xpath('//div[@class="tkp_content"]//p/text()').extract()
        field = response.xpath('//div[@class="path"]/a/text()').extract()
        if len(title) == 0 or len(texts) == 0:
            print('此链接未解析出标题或内容:[%s]' % response.url)
            return
        if len(field) == 0:
            field = ['', '其他']
        item['url'] = response.url
        item['field'] = time.strftime("%Y%m%d") + os.sep + field[1]
        item['title'] = ''.join(title[0].split())
        item['content'] = texts
        # print(texts)
        print('dump item:   ', item['url'])
        yield item

    def parse_article1(self, response):
        print('Enter parse_article')
        item = DagongwItem()
        title = response.xpath('//head/title/text()').extract()
        texts = response.xpath('//div[@class="tpk_text clearfix"]//p/text()').extract()
        # field = response.xpath('//div[@class="path"]/a/text()').extract()
        if len(title) == 0 or len(texts) == 0:
            print('此链接未解析出标题或内容:[%s]' % response.url)
            return
        item['url'] = response.url
        item['field'] = time.strftime("%Y%m%d") + os.sep + '宗教人文和体育类'
        item['title'] = ''.join(title[0].split())
        item['content'] = texts
        # print(texts)
        print('dump item:   ', item['url'])
        yield item



