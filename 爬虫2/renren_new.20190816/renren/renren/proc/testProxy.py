import json
import time

import requests

ip_url = r'http://mvip.piping.mogumiao.com/proxy/api/get_ip_bs?appKey=261729aeb3884342a0019acaa103fe18&count=5&expiryDate=0&format=1&newLine=2'
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    # 'Cookie': 'td_cookie=180202120; td_cookie=180121702',
    'Host': 'mvip.piping.mogumiao.com',
    # 'Referer': 'http://mvip.piping.mogumiao.com/proxy/api/get_ip_bs?appKey=261729aeb3884342a0019acaa103fe18&count=5&expiryDate=0&format=1&newLine=2',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}

ip_pool = list()


def get_proxy():
    while True:
        resp = requests.get(ip_url, headers=headers)
        print(resp.status_code)
        print(resp.text)

        if resp.status_code != 200:
            time.sleep(2)
            continue
        try:
            json_data = json.loads(resp.text)
            if int(json_data['code']) != 0:
                time.sleep(2)
                continue

            for data in json_data['msg']:
                proxies = {
                    'http': r'http://' + data["ip"] + ':' + data["port"],
                    'https': r'https://' + data["ip"] + ':' + data["port"],
                }
                print(proxies)
                ip_pool.append(proxies)
            break
        except Exception as e:
            time.sleep(2)
            continue


def run():
    get_proxy()
    # while len(ip_pool) > 0:
    #     proxies = ip_pool[0]
    #     ip_pool.pop()
    #
    #     res = requests.get(url='http://httpbin.org/get', proxies=proxies, verify=False)
    #     print(res.text)

    proxies = ip_pool[0]
    ip_pool.pop()

    res = requests.get(url='http://httpbin.org/get', proxies=proxies, verify=False)
    # print(res.text)
    if res.status_code == 200:
        print("pass ")

    print('sleeping ...')
    time.sleep(10)
    ip_pool.clear()
    get_proxy()
    proxies_2 = ip_pool[0]

    time.sleep(20)
    print('sleeping ...')

    res = requests.get(url='http://httpbin.org/get', proxies=proxies, verify=False)
    # print(res.text)
    if res.status_code == 200:
        print("## pass old")
    else:
        print("old fail ",proxies)

    time.sleep(3)

    res = requests.get(url='http://httpbin.org/get', proxies=proxies_2, verify=False)
    # print(res.text)
    if res.status_code == 200:
        print("## pass new")
    else:
        print("new fail",proxies_2)


if __name__ == '__main__':
    run()
