# -*- coding: utf-8 -*-
import json
import re

import pymongo
from scrapy.exceptions import DropItem


class HtmlCleanPipelin(object):

    def process_item(self, item, spider):
        content = item['content']
        # 删除无用元素
        content = re.sub(r'<table.*?">.*?</table>', '', content)
        content = re.sub(r'<iframe.*?">.*?</iframe>', '', content)
        # content = re.sub(r'<img.+?>', '', content)

        # 删除div标签
        # result = re.subn(r'<div.+?>(.+)</div>', '\g<1>', content)
        # while result[1] > 0:
        #     content = result[0]
        #     result = re.subn(r'<div.+?>(.+)</div>', '\g<1>', content)
        # 删除责编 TODO 并不能删除该标签
        # content = re.sub('<p class="res-edit">.+?</p>', '', content)

        # 删除超链接
        # content = re.sub(r'<a.+?>(.+?)</a>', '\g<1>', content)
        # 删除span标签
        # content = re.sub(r'<span.+?>(.*?)</span>', '\g<1>', content)
        # 删除p标签
        # content = re.sub(r'<p.*?>', '', content)
        # content = re.sub(r'</p>', '\n', content)
        # 删除注释，换行，空格
        # content = re.sub(r'(<!--.*?-->|[ \r\n]|<br>|\u2003|\u3000)+', ' ', content)
        # 删除前导空格
        if content[0] == ' ':
            content = content[1:]
        # item['content'] = Selector(text=content).css('#ContentBody::text').extract_first()
        item['content'] = content
        return item


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
