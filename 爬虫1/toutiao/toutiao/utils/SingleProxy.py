APP_KEY = '261729aeb3884342a0019acaa103fe18'
IP_PORT = 'transfer.mogumiao.com:9001'

proxy = {"http": "http://" + IP_PORT, "https": "https://" + IP_PORT}
headers = {"Proxy-Authorization": 'Basic ' + APP_KEY}


def get_proxy():
    return proxy, headers
