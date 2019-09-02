# -*- coding: utf-8 -*-
import logging
import re

import scrapy
import time
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from qudong.items import QudongItem
from qudong.utils.setting import VISIT_URL_PATH
from qudong.utils.tools import Pretty, get_function_name
from qudong.utils.url_manager import UrlManager

logger = logging.getLogger()


class CqudongSpider(CrawlSpider):
    name = 'cqudong'
    allowed_domains = ['qudong.com']
    start_urls = ['https://app.qudong.com/map.php',
                  'https://www.qudong.com/',
                  ]

    rules = (
        Rule(LinkExtractor(allow=r'(http|https)://\w+\.qudong\.com/[\d\w]+/$'),
             follow=True),
        Rule(LinkExtractor(allow=r'(http|https)://\w+\.qudong\.com/[\w\d]+/[\w\d]+/$'),
             follow=True),
        Rule(LinkExtractor(allow=r'[http|https]://[\w\d]+\.qudong\.com/[\d\w]+/\d+\.shtml'),
             callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'(http|https)://\w+\.qudong\.com/\d+/\d+/\d+\.shtml'),
             callback='parse_item', follow=True),
    )

    pretty = Pretty()
    url_manager = UrlManager()
    url_manager.load(VISIT_URL_PATH)
    # 提取域名中前缀
    re_prefix = re.compile(r'(http|https)?://(?P<field>[\w\d]+)\.')

    def parse_item(self, response):
        logger.info("parse ...................        {}".format(response.url))

        # 更新已访问url
        if self.url_manager.url_exist(response.url):
            logger.info("visited url    {}".format(response.url))
            return
        self.url_manager.add_url(response.url)
        self.url_manager.update()

        try:
            # 提取域名为文件夹名
            field = self.re_prefix.search(response.url).group('field') or "NoneType"

            # 提取标题为文件名 标题为空 用时间代替
            title = response.xpath("//div[re:match(@class,'wenzhang')]/h1/text()").extract_first()
            title = self.pretty.pretty_title(title)
            if title is None or len(title) == 0:
                title = time.strftime("%Y%m%d_%H%M%S")

            # 清洗内容 用<p>通用性更强
            content = response.xpath("//p/text()").extract()
            content = "\r\n".join(self.pretty.pretty_contents(content))
            # 内容为空返回
            if content is None or len(content) == 0:
                return

            item = QudongItem()
            item['url'] = response.url
            item['field'] = field
            item['title'] = title
            item['content'] = content

            logger.info("get item {}".format(item))
            return item
        except Exception as e:
            logger.error("{}    [ERROR]:{}".format(get_function_name(), e))
