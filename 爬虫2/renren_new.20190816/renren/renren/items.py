# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RenrenItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class RenrenStatusItem(scrapy.Item):
    url = scrapy.Field()
    field = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()


class RenrenBlogItem(scrapy.Item):
    spider = scrapy.Field()
    url = scrapy.Field()
    field = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
