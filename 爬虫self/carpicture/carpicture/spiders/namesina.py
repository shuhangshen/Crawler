# -*- coding: utf-8 -*-
import scrapy
from carpicture.items import NamesinaItem

class NamesinaSpider(scrapy.Spider):
    name = 'namesina'
    allowed_domains = ['sina.com.cn']
    # start_urls = ['http://sina.com.cn/']
    start_urls = ['http://db.auto.sina.com.cn/list-1-0-0-0-0-0-0-0-9-0-1.html']

    def parse(self, response):
        title = response.xpath('//dt/a/text()').extract()
        item = NamesinaItem()
        item['title'] = title
        yield item



