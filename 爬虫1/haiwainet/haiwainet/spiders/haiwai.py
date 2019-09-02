# -*- coding: utf-8 -*-
import logging
import re

import scrapy
import time
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from haiwainet.items import HaiwainetItem
from haiwainet.pipelines import get_function_name
from haiwainet.url_manager import UrlManager

logger = logging.getLogger()


class HaiwaiSpider(CrawlSpider):
    name = 'haiwai'
    allowed_domains = ['haiwainet.cn']
    start_urls = ['http://www.haiwainet.cn/map/']

    rules = (
        # Rule(LinkExtractor(allow=r'http://www\.haiwainet\.cn/map/'),  follow=True),
        Rule(LinkExtractor(allow=r'http://([\w]+)\.haiwainet\.cn/n/\w+/\w+/c(\d+)-(\d+)\.html$'),
             callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'[\d]+\.html$'), follow=True),
        Rule(LinkExtractor(allow=r'http://[\w\d]+\.haiwainet\.cn/[\w\d]+/[\d]+\.html$'), follow=True),

        Rule(LinkExtractor(allow=r'http://([\w]+)\.haiwainet\.cn/([\w\d]+)?$'), follow=True),
        Rule(LinkExtractor(allow=r'http://([\w]+)\.haiwainet\.cn/([\w\d]+)/$'), follow=True),
    )

    re_titleRep = re.compile(r'[\*#|:：;；\-\+" ]')
    re_vchar = re.compile(r'[&$^*#|·]')

    url_manager = UrlManager()
    url_manager.load("Z:\\lisi8\\WORKSPACE\\haiwainet\\visit_url.txt")

    def pretty_contents(self, strings):
        """整理字符串"""
        rets = []
        for string in strings:
            ret = re.sub(self.re_vchar, " ", string)
            ret = ret.strip()
            if ret is not None and len(ret) != 0:
                rets.append(ret)
        return rets

    def parse_item(self, response):
        logger.info("parse ...................        {}".format(response.url))
        # logger.info("body {}".format(response.body.decode('utf-8')))

        if self.url_manager.url_exist(response.url):
            logger.info("visited url    {}".format(response.url))
            return
        self.url_manager.add_url(response.url)
        self.url_manager.update()

        try:
            field = response.xpath("//div[@class='fl'][2]/a/text()").extract() or "NoneType"
            field = "".join(field)

            title = response.xpath("//h1[@class='show_wholetitle']/text()").extract_first()
            if title is None or len(title) ==0:
                title = time.strftime("%Y%m%d_%H%M%S")
            else:
                title = re.sub(self.re_titleRep, "", title)

            content = response.xpath("//p/text()").extract()
            content = "\r\n".join(self.pretty_contents(content))

            item = HaiwainetItem()
            item['field'] = field
            item['url'] = response.url
            item['title'] = title
            item['content'] = content

            logger.info("get item {}".format(item))
            return item
        except Exception as e:
            logger.error("{}    [ERROR]:{}".format(get_function_name(), e))
