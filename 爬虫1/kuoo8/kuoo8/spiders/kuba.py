# -*- coding: utf-8 -*-
import logging
import scrapy
import time
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from kuoo8.items import Kuoo8Item
from kuoo8.utils.setting import VISIT_URL_PATH
from kuoo8.utils.tools import Pretty
from kuoo8.utils.url_manager import UrlManager

logger = logging.getLogger()


class KubaSpider(CrawlSpider):
    name = 'kuba'
    allowed_domains = ['kuoo8.com']
    start_urls = ['http://www.kuoo8.com/news/kfx.html',
                  'http://www.kuoo8.com/news/keji.html',
                  'http://www.kuoo8.com/news/gaoji.html',
                  'http://www.kuoo8.com/news/huaijiu.html',
                  'http://www.kuoo8.com/news/zhishi.html',
                  'http://www.kuoo8.com/news/chushi.html',
                  'http://www.kuoo8.com/news/duanzi.html',
                  'http://www.kuoo8.com/news/meituwen.html',
                  ]

    rules = (
        Rule(LinkExtractor(allow=r'^\w+_\d+\.html'), follow=True),

        Rule(LinkExtractor(allow=r'http://kuoo8\.com/\w+/([\w\d_]+)\.html',
                           deny_domains=r'http://kuoo8\.com/[html|QQbiaoqing]/'),
             callback='parse_item', follow=True),
    )

    pretty = Pretty()
    url_manager = UrlManager()
    url_manager.load(VISIT_URL_PATH)

    def parse_item(self, response):
        logger.info("parse ...................        {}".format(response.url))

        # get update url_manager
        if self.url_manager.url_exist(response.url):
            logger.info("visited url    {}".format(response.url))
            return
        self.url_manager.add_url(response.url)
        self.url_manager.update()

        field = response.xpath("//div[@class='longTop']/a[2]/text()").extract_first()

        title = response.xpath("//h1[@class='workTitle']/text()").extract_first()
        title = self.pretty.pretty_title(title)
        if title is None or len(title) == 0:
            title = time.strftime("%Y%m%d_%H%M%S")

        # content = response.xpath("//div[re:match(@class,'workContent')]/p/text()").extract()
        content = response.xpath("//p/text()").extract()
        content = "\r\n".join(self.pretty.pretty_contents(content))

        item = Kuoo8Item()
        item['url'] = response.url
        item['field'] = field
        item['title'] = title
        item['content'] = content

        if item['content'] is None or len(item['content']) == 0:
            return

        logger.info("get item {}".format(item))
        return item
