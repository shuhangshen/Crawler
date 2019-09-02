import logging
import sqlite3

logger = logging.getLogger()

# sqlite pipeline

class SQLitePipeline(object):
    def __init__(self, dbname):
        self.dbname = dbname

    @classmethod
    def from_crawler(cls, crawler):
        return cls(dbname=crawler.settings.get('DBNAME'))

    def open_spider(self, spider):
        if spider.name not in self.accept_spider:
            logger.info("failue spider [name] {} ".format(spider.name))
            return

        self.conn = sqlite3.connect(self.dbname)
        self.cx = self.conn.cursor()

    def process_item(self, item, spider):
        if spider.name not in self.accept_spider:
            logger.info("failue spider [name] {} ".format(spider.name))
            return

        data = dict(item)
        keys = ','.join(data.keys())
        values = ','.join(['%s'] * len(data))
        sql = 'insert into TableName(%s) values (%s)' % (keys, tuple(data.values()))
        self.cx.execute(sql)
        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.conn.close()
