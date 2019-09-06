import logging
import os

from .tools import get_function_name
from .setting import ALLOW_SPIDER, DATA_PATH

logger = logging.getLogger()
base_path = DATA_PATH

# 文本 pipeline


class WriteFilePipeline(object):
    """
    确认Field 参数
    field
    title
    url
    content
    保存文件 pipeline
    """

    accept_spider = ALLOW_SPIDER

    def __make_dir(self, path):
        """
        Make_Dir
        """
        if not os.path.exists(path):
            os.makedirs(path)

    def process_item(self, item, spider):
        if spider.name not in self.accept_spider:
            logger.info("failue spider [name] {} ".format(spider.name))
            return

        save_path = DATA_PATH
        if "spider" in item:
            save_path = os.path.join(save_path, item['spider'])
        dir_path = os.path.join(save_path, item['field'])

        self.__make_dir(dir_path)
        save_file_path = dir_path + os.path.sep + item['title'] + '.txt'
        logger.info("{}  save:   {}".format(get_function_name()
                                            , save_file_path))
        # 已按路径保存的文件
        if os.path.exists(save_file_path):
            logger.info("{} item exist".format(get_function_name()))
            return item

        logger.info("current save path  {}".format(save_file_path))
        with open(save_file_path, 'w', encoding='utf-8') as file:
            file.write(item['url'] + '\r\n')
            file.write(item['title'] + '\r\n')
            file.write(item['content'])

        return item
