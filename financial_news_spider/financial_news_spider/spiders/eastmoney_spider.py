import json
import re
from urllib.parse import urlparse, parse_qs
import scrapy
from scrapy.selector import Selector
from bs4 import BeautifulSoup


from ..items import NewsItem


class EastmoneySpider(scrapy.Spider):
    """spider for 东方财富网."""
    name = 'east_money'
    start_url = 'http://so.eastmoney.com/Web/GetSearchList?type=20&pageindex=%d&pagesize=200&keyword=%s'

    companies = [
        '特锐德',
        '神州泰岳',
        '乐普医疗'
    ]

    def start_requests(self):

        for company in self.companies:
            url = self.start_url % (1, company)
            yield scrapy.Request(url=url, callback=self.parse, meta={
                'proxy': '117.23.56.4:808'  # 校园网访问搜索页面需要代理
            })

    def parse(self, response):
        search_result = json.loads(response.text)
        if search_result['IsSuccess']:
            total_page = search_result['TotalPage']
            total_count = search_result['TotalCount']
            keyword = parse_qs(urlparse(response.request.url).query)['keyword'][0]
            page_index = re.search('pageindex=(\d+)', response.request.url).group(1)

            # current search result page
            for article in search_result['Data']:
                meta = {
                    'company': keyword,
                    'title': article['Art_Title'],
                    'time': article['Art_CreateTime']
                }
                yield response.follow(article['Art_Url'], callback=self.parse_news, meta=meta)

            # other search result page
            if page_index == '1':
                self.log('company %s total page %d total count %d' % (keyword, total_page, total_count))
                for i in range(2, int(total_page) + 1):
                    url = self.start_url % (i, keyword)
                    # self.log('search page %d: %s' % (i, url))
                    yield response.follow(url, callback=self.parse, meta={
                        'proxy': response.request.meta['proxy']
                    })

    def parse_news(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        content = soup.find(id='ContentBody')
        # 访问全文
        if content.find(class_='pagesize') is not None:
            url = response.request.url.replace('.html', '_0.html')
            yield response.follow(url, callback=self.parse_news, meta=response.meta)
        else:
            for span in content.find_all('span'):
                if span.string is None:
                    span.decompose()
                else:
                    span.unwrap()
            for br in content.find_all('br'):
                br.replace_with('\n')
            for a in content.find_all('a'):
                a.unwrap()
            for table in content.find_all('table'):
                table.replace_with('\n')
            self.delete_tag(content, tagname='img')
            self.delete_tag(content, tagname='script')
            self.delete_tag(content, class_='abstract')    # 摘要标题
            self.delete_tag(content, class_='b-review')    # 摘要内容
            self.delete_tag(content, class_='reading')     # 阅读资料
            self.delete_tag(content, class_='res-edit')    # 责任编辑
            self.delete_tag(content, class_='res-title')   # 原标题

            item = NewsItem()
            item['title'] = re.sub(r'</?em>', '', response.meta['title'])
            item['time'] = response.meta['time']
            item['company'] = response.meta['company']
            item['url'] = response.request.url
            item['content'] = content.get_text(strip=True)
            if item['content'] is not None:
                yield item

    @staticmethod
    def delete_tag(node, tagname=None, class_=None):
        if tagname is not None:
            for tag in node.find_all(tagname):
                tag.decompose()
        if class_ is not None:
            for tag in node.find_all(class_=class_):
                tag.decompose()
