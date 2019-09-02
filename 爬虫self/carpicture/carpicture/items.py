# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

'''
class CarpictureItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    collection = table = "picture"
    images = scrapy.Field()
    title = scrapy.Field()
    image_paths = scrapy.Field()
    image_urls = scrapy.Field()
    # image_results = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
'''


class QqautoItem(scrapy.Item):
    collection = table = "picture"
    images = scrapy.Field()
    title = scrapy.Field()
    image_paths = scrapy.Field()
    image_urls = scrapy.Field()
    # image_results = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()


class SinaautoItem(scrapy.Item):
    # collection = table = "picture"
    images = scrapy.Field()
    title = scrapy.Field()
    image_paths = scrapy.Field()
    image_urls = scrapy.Field()
    # image_results = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()


class AutohomeItem(scrapy.Item):
    # collection = table = "picture"
    images = scrapy.Field()
    title = scrapy.Field()
    image_paths = scrapy.Field()
    image_urls = scrapy.Field()
    # image_results = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()


class BaiduimageItem(scrapy.Item):
    collection = table = "picture"
    images = scrapy.Field()
    title = scrapy.Field()
    image_paths = scrapy.Field()
    image_urls = scrapy.Field()
    # image_results = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()

class NamesinaItem(scrapy.Item):
    title = scrapy.Field()