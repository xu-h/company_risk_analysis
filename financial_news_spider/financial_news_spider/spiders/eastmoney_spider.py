import json
import re
from urllib.parse import urlparse, parse_qs
import scrapy
from scrapy.selector import Selector

from ..items import NewsItem


class EastmoneySpider(scrapy.Spider):
    """spider for 东方财富网."""
    name = 'east_money'

    def start_requests(self):
        companies = [
            '宝胜股份'
        ]
        url = 'http://so.eastmoney.com/Web/GetSearchList?type=20&pagesize=10&keyword='

        for company in companies:
            yield scrapy.Request(url=url + company, callback=self.parse)

    def parse(self, response):
        search_result = json.loads(response.text)
        if search_result['IsSuccess']:
            total_page = search_result['TotalPage']
            total_count = search_result['TotalCount']
            keyword = parse_qs(urlparse(response.request.url).query)['keyword'][0]
            self.log('company %s total page %d total count %d' % (keyword, total_page, total_count))
            for article in search_result['Data']:
                # self.log('find artical ' + article['Art_Title'])
                # self.log('news url: ' + article['Art_Url'])
                meta = {
                    'company': keyword,
                    'title': article['Art_Title'],
                    'time': article['Art_CreateTime']
                    # 'proxy': '127.0.0.1:1080'  # 校园网访问需要代理
                }
                request = response.follow(article['Art_Url'], callback=self.parse_news, meta=meta)
                yield request

    def parse_news(self, response):
        item = NewsItem()
        item['title'] = re.sub(r'</?em>', '', response.meta['title'])
        item['time'] = response.meta['time']
        item['company'] = response.meta['company']
        item['url'] = response.request.url

        content = response.css('#ContentBody').extract_first()
        # 删除div标签
        result = re.subn(r'<div.+?>(.+)</div>', '\g<1>', content)
        while result[1] > 0:
            content = result[0]
            result = re.subn(r'<div.+?>(.+)</div>', '\g<1>', content)
        # 删除无用元素
        content = re.sub(r'<table.*?">.*?</table>', '', content)
        content = re.sub(r'<iframe.*?">.*?</iframe>', '', content)
        # content = re.sub(r'<img.+>', '', content)
        # 删除责编 TODO 并不能删除该标签
        content = re.sub('<p class="res-edit">.+?</p>', '', content)

        # 删除超链接
        content = re.sub(r'<a.+?>(.+?)</a>', '\g<1>', content)
        # 删除span标签
        content = re.sub(r'<span.+?>(.*?)</span>', '\g<1>', content)
        # 删除p标签
        content = re.sub(r'<p.*?>', '', content)
        content = re.sub(r'</p>', '\n', content)
        # 删除注释，换行，空格
        content = re.sub(r'(<!--.*?-->|[ \r\n]|<br>|\u2003|\u3000)+', ' ', content)
        # 删除前导空格
        if content[0] == ' ':
            content = content[1:]
        item['content'] = content
        yield item
