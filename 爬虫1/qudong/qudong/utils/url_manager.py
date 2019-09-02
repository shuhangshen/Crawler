# -*- coding: utf-8 -*-


class UrlManager(object):
    """
    txt记录爬取成功的url并判别重复
    """
    url_set = set()
    url_tmp = set()
    tmp_size = 100
    path = ""

    def url_exist(self, url):
        """
        是否已爬取的url
        :param url: 待判别url
        :return:是否
        """
        return url in self.url_set

    def add_url(self, url):
        """
        增加url记录
        :param url:待加入url
        :return: null
        """
        if url is None or len(url) == 0:
            return
        if not self.url_exist(url):
            self.url_tmp.add(url)
            self.url_set.add(url)
        else:
            print("exists")

    def update(self):
        """
        更新url保存
        :return:
        """
        if len(self.url_tmp) >= self.tmp_size:
            self.save()

    def load(self, path):
        """
        从txt加载url记录
        :param path:
        :return:
        """
        with open(path, 'a+', encoding='utf-8') as file:
            self.path = path
            file.seek(0)
            for line in file.readlines():
                line = line.strip()
                if len(line) != 0:
                    self.url_set.add(line)
                    #print("?    {}".format(line))

    def save(self):
        """
        保存缓存到txt
        :return:
        """
        with open(self.path, 'a+', encoding='utf-8') as file:
            file.writelines(line + "\r\n" for line in self.url_tmp)
            self.url_tmp.clear()

    def print(self):
        """
        打印记录
        :return:
        """
        print("url_exists   {}".format(self.url_set))


if __name__ == "__main__":
    url_manager = UrlManager()
    url_manager.load("C:\\WORKSPACE\\takungpao\\visit_url.txt")
    url_manager.print()
    url_manager.add_url("123")
    url_manager.add_url("1234")
    url_manager.add_url("12345")
    url_manager.add_url("12347")
    url_manager.save()
    print(url_manager.url_exist("123"))
