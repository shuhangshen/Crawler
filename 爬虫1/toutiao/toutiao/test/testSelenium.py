from scrapy.http import HtmlResponse
from selenium import webdriver


def run():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    browser = webdriver.Chrome(chrome_options=chrome_options)
    browser.get('http://www.baidu.com/')
    content = browser.page_source
    browser.quit()

    print(content)


if __name__ == '__main__':
    run()
