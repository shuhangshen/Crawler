import time

from common.proxy.proxy_client import ProxyClient


def test_cli():
    cli = ProxyClient()
    proxy = cli.take_proxy()
    print("result ", proxy)
    time.sleep(20)
    proxy2 = cli.take_proxy()
    print("result ", proxy2)


if __name__ == '__main__':
    test_cli()
