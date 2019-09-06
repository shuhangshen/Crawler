# -*- coding: utf-8 -*-
import scrapy
import re
import logging
from Hupu.utils.try_except import try_except
from Hupu.items import HupuItem
from scrapy import Request

logger = logging.getLogger()


class HupuSpider(scrapy.Spider):
    name = 'hupu'
    allowed_domains = ['hupu.com']
    start_urls = ['https://bbs.hupu.com/boards.php']
    # start_urls = ['https://bbs.hupu.com/29238100.html']

    match_char = re.compile(r'[ ?/":*<>|]+')
    match_page = re.compile(r'-(.*).html')
    match_num = re.compile(r'\d+')
    sub_num = re.compile(r'.html')

    default_cookies = {'_dacevid3': '2bd07c80.78b8.19ae.a1ae.a106ef4a0f2d',
                       '_cnzz_CV30020080': 'buzi_cookie%7C2bd07c80.78b8.19ae.a1ae.a106ef4a0f2d%7C-1', '__gads': 'ID',
                       'PHPSESSID': '3b52d51b6a0c7904d295894fb1a19765',
                       'sensorsdata2015jssdkcross': '%7B%22distinct_id%22%3A%2216cf524f06f176-01b9537266640b-3c375f0d-2073600-16cf524f07139e%22%2C%22%24device_id%22%3A%2216cf524f06f176-01b9537266640b-3c375f0d-2073600-16cf524f07139e%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D',
                       '_HUPUSSOID': '2f8aed96-b09f-4f39-9763-19e0b63df745', 'forumcode3803': 'a55e8120ea80162dc563e93851132700',
                       '_fmdata': 'J2YEzwAK95loTemCCzuuTILXN9UMHmNlNKyyqfop9gTwBkWf4M8OXLNdYiJO7Utl9W2edr6wbXzL3zOOc%2FOgxGa%2FvLAK2jAPbhHa83XKYpA%3D',
                       'forumcode4972': '432426f93b43dff390afcbde982b317f', '_CLT': 'b0c2a05996d8b48b354e1fa4ddfc1fef',
                       'u': '54466387|6JmO5omRSlIxNzIwODQ1NjIx|3b50|d2ef1c77518f2a1a16eeb966143a061e|518f2a1a16eeb966|aHVwdV81ZmQ2YzNkOTBhYWUwYmE2',
                       'us': '8eb160639f5ffb7d3b92f81930c31bfc9ab68d825808461c4499da1103628e62bfc142878af82adb39bc3f6e75b886a42d3da430ee82b4150c5164f01adfcc42',
                       'ua': '17813272', 'Hm_lvt_39fc58a7ab8a311f2f6ca4dc1222a96e': '1567566637,1567567313,1567567332,1567567894',
                       'Hm_lpvt_39fc58a7ab8a311f2f6ca4dc1222a96e': '1567567894', '__dacevst': 'eca84bd0.ebc51017|1567569701705'
                       }

    default_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        "Accept-Language": 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Host': 'www.dianping.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    def __init__(self):
        print('Enter Init ------')
        super(HupuSpider, self).__init__()
        self.num = 1

    def __del__(self):
        print("Exit ------")

    def parse(self, response):
        links = response.xpath('//div[@class="plate_03_list"]')
        # forums = links.xpath('./h3/text()').extract()
        urls = links.xpath('./ul/li/a/@href').extract()
        # print(urls)
        urls_topics = links.xpath('./ul/li/a/text()').extract()
        # print(urls_topics)
        for url in urls:
            link = 'https://bbs.hupu.com' + url
            try:
                yield Request(url=link, meta={'key': url}, callback=self.parse_topic)
            except Exception as e:
                logger.error('{}:parse failed, Reason: {}'.format(response.url, e))

    def parse_topic(self, response):
        key = response.meta['key']
        forum = response.xpath('//div[@class="breadCrumbs"]/a[2]/text()').extract_first()
        topic = response.xpath('//head/title/text()').extract_first().split('-')[0]
        print('---开始解析: {}>>{}---'.format(forum, topic))
        links = response.xpath('//div[@class="titlelink box"]/a[@class="truetit"]/@href').extract()
        if len(links) == 0:
            print('{}: 没有帖子------'.format(response.url))
            logger.info('{}:没有帖子，或者加密了------'.format(response.url))
            self.num = 1
            return
        for link in links:
            url = 'https://bbs.hupu.com' + link
            try:
                yield Request(url=url, meta={'html': link}, callback=self.parse_content)
            except Exception as e:
                logger.error('{}:parse failed, Reason: {}'.format(response.url, e))
        #循环翻页
        self.num += 1
        url = 'https://bbs.hupu.com{}-{}'.format(key, self.num)
        try:
            yield Request(url=url, cookies=self.default_cookies, meta={'key': key}, callback=self.parse_topic)
        except Exception as e:
            logger.error('{}:parse failed, Reason: {}'.format(response.url, e))

    @try_except
    def parse_content(self, response):
        # html = /.234567.html
        html = response.meta['html']
        item = HupuItem()
        structure = response.xpath('//div[@class="bbs_head"]/div[@class="breadCrumbs"]/a/text()').extract()
        if len(structure) == 0:
            logger.error('{}:此页无内容，或为解析出来'.format(response.url))
            print('{}:未解析出来'.format(response.url))
            return
        image_links = response.xpath('//div[@class="quote-content"]/p/img/@src').extract()
        titlec = response.xpath('//head/title/text()').extract_first()
        titles = titlec.strip().split('-')[0]
        title = re.sub(self.match_char, '-', titles)
        floor_list = response.xpath('//form[@name="delatc"]')
        content = []
        # 提取floor_list每一级目录下的文字
        for floor in floor_list:
            content_list = floor.xpath('string(.)').extract_first()
            # print(content_list)
            for i in content_list.split('\n'):
                if i != '':
                    content.append(i)
        if len(title) == 0 or len(content) == 0:
            logger.error("{}:此链接解析失败".format(response.url))
            print('{}:解析失败'.format(response.url))
        item['image_urls'] = image_links
        item['url'] = response.url
        item['forum'] = structure[1]
        item['topic'] = structure[-1]
        item['title'] = title
        item['content'] = content
        yield item

        # 循环翻页
        page_re = response.xpath('//div[@class="bbs-hd-h1"]/span/span/text()').extract_first()
        # print(page_re)
        page_num = re.findall(self.match_num, page_re)[0]
        if int(page_num) <= 20:
            return
        page = int(page_num) // 20
        # print(page)
        key = re.findall(r'-', response.url)
        if not key:
            new_html = re.sub(self.sub_num, '-2.html', html)
            print("Request Url: {}".format(response.url))
            url = 'https://bbs.hupu.com' + new_html
            yield Request(url=url, cookies=self.default_cookies, meta={'html': html}, callback=self.parse_content)
        num = re.findall(self.match_page, response.url)[0]
        if int(num) < page:
            print("Request Url: {} >> title:{}".format(response.url, title))
            # print(num)
            page_num = int(num) + 1
            url = re.sub(self.match_page, '-' + str(page_num) + '.html', response.url)
            yield Request(url=url, cookies=self.default_cookies, meta={'html': html}, callback=self.parse_content)

