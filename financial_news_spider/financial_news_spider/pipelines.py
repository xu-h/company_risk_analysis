# -*- coding: utf-8 -*-
import json
import pymongo
from bs4 import BeautifulSoup


class JsonWriterPipeline(object):
    file = None

    def open_spider(self, spider):
        self.file = open('items.json', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


class MongoPipeline(object):

    collection_name = 'company_news'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        # 每次启动清空数据库
        self.db.drop_collection(self.collection_name)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item


class TxtPipeline(object):

    def __init__(self, filename):
        self.filename = filename
        self.file = None
        self.cnt = 0

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            filename=crawler.settings.get('TXT_FILENAME')
        )

    def open_spider(self, spider):
        self.file = open(self.filename, 'w', encoding='UTF-8')
        self.file.close()

    def close_spider(self, spider):
        # self.file.close()
        pass

    def process_item(self, item, spider):
        self.file = open(self.filename, 'a', encoding='UTF-8')
        self.file.write('##########\n')
        self.file.write(str(self.cnt) + '\n')
        self.file.write(item['title'] + '\n')
        self.file.write(item['company'] + '\n')
        self.file.write(item['time'] + '\n')
        self.file.write(item['url'] + '\n')
        self.file.write(item['content'] + '\n')
        self.file.close()
        self.cnt += 1
        return item
