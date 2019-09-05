import scrapy
from scrapy import Request
from scrapy.crawler import CrawlerProcess
from dagongw.utils.tools import print_html_body
import re

class TextSpider(scrapy.Spider):
    name = 'text'
    allowed_domains = ['takungpao.com']
    # start_urls = ['http://takungpao.com/']
    host = 'http://www.takungpao.com/'
    start_urls = ['http://www.takungpao.com/']

    # 爬取领域
    fields = [
        'news',
        'opinion',
        'lens',
        'finance',
        'culture',
        'life',
        'special',
    ]

    default_header = {
        'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        "Accept-Language": 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Host': 'www.takungpao.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
         (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',
    }

    # 网址匹配
    pat = r'(((http|ftp|https)://)(([a-zA-Z0-9\._-]+\.[a-zA-Z]{2,6})|([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}))\
      (:[0-9]{1,4})*(/[a-zA-Z0-9\&%_\./-~-]*)?)'
    re_url = re.compile(pat)

    def parse_url(self, response):
        links = response.xpath("//div[@class='list']//u1[class='clearfix']//li/a/@href")
        for link in links:
            url = re.findall(self.re_url, link)[0]
            print(url)

        # 获取各个栏目如"中国、港闻..."等的URL
        def get_url_request(self, response):
            sel = scrapy.Selector(response)
            links_in_a_page = sel.xpath('//a[@href]')
            for link_sel in links_in_a_page:
                item = DagongwItem()
                link = str(link_sel.re('href="(.*?)"')[0])
                if link:
                    if not link.startswith('http'):
                        link = "http://www.takungpao.com" + response.url
                    try:
                        yield Request(link, callback=self.get_url_request)
                        item['url'] = link
                    except Exception as e:
                        print("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))
                        logger.error(
                            "{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))

            '''
            links = response.xpath("u1[@class='clearfix']//li/a/@href")
            for link in links:
                url = str(link.re('href="(.*?)"')[0])
                yield Request(url=url, callback=self.get_url_request)
            '''

        # 向“中国、港闻、...”等网站发起请求，获取其中每页的URL
        def get_url(self, response):
            try:
                links = response.xpath('//div[@class="tkp_page"]/a/@href')
                for link in links:
                    all_url = "http://www.takungpao.com" + link
                    return all_url

            except Exception as e:
                print("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))
                logger.error("{} request URL {} failure Reason  {}".format(get_function_name(), response.url, e))

        # 发起爬取请求
        def start_request(self, response):
            links = response.xpath('//dl[@class="item clearfix"]//dt/a/@href')
            for link in links:
                request_url = link
                yield Request(url=request_url, callback=self.parse_article)

        # URL进去直接是文章
        def parse_article(self, response):
            print('Enter parse_article')

            title = response.xpath('//head/title/text()').extract()
            texts = response.xpath('//div[class="tkp_content"/p/text()').extract()
            field = response.xpath('//div[@class="path"/a/text()').extract()

            item['url'] = response.url
            item['field'] = time.strftime("%Y%m%d") + os.sep + field[1]
            item['title'] = ''.join(title[0].split())
            item['content'] = texts
            print('dump item:   ', item['url'])
            yield item

def run():
    process = CrawlerProcess()
    process.crawl(TextSpider)
    process.start()


if __name__ == '__main__':
    run()

