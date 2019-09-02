import redis


#  封装 redis 操作

class RedisHelper(object):
    """
    redis 操作封装
    """
    host = ''
    port = 0

    def __init__(self, *, host, port):
        self.host = host
        self.port = port
        self.redis_cli = redis.Redis(host=host, port=port)

    def bitmap_set(self, value=1, *, key, offset):
        """
        bitmap 去重 set1 或set0
        :param value:
        :param key:
        :param offset:
        :return:
        """
        return self.redis_cli.setbit(key, offset, value)

    def bitmap_contains(self, *, key, offset):
        """
        bitmap 去重 是否包含
        :param key:
        :param offset:
        :return:
        """
        return self.redis_cli.getbit(key, offset)

    def list_insert(self, *, key, elem):
        """
        列表插入元素
        :param key:
        :param elem:
        :return:
        """
        self.redis_cli.lpush(key, elem)

    def list_take(self, *, key):
        """
        获取首端元素
        :param key:
        :return:
        """
        if self.redis_cli.exists(key) and self.redis_cli.llen(key) > 0:
            return self.redis_cli.lpop(key)
        return None

    def list_get(self, *, key):
        if self.redis_cli.exists(key):
            list_len = self.redis_cli.llen(key)
            if list_len > 0:
                return self.redis_cli.lrange(key, 0, list_len)
        return None

    def list_remove(self, *, key, value):
        if self.redis_cli.exists(key) and self.redis_cli.llen(key) > 0:
            return self.redis_cli.lrem(key, 0, value)
        return None

    def list_len(self, *, key):
        return self.redis_cli.llen(key)

    def exists(self, *, key):
        """
        容器是否存在
        :param key:
        :return:
        """
        return self.redis_cli.exists(key)

    def remove(self, *, key):
        """
        移除容器
        :param key:
        :return:
        """
        self.redis_cli.delete(key)


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 6379
    redis_helper = RedisHelper(host=host, port=port)
    list_name = "goods"
    redis_helper.list_insert(key=list_name, elem="hello")
    redis_helper.list_insert(key=list_name, elem="world")
    print("get : ", *redis_helper.list_zip(key=list_name))
    for k, v in redis_helper.list_zip(key=list_name):
        print(k, v)
