# import json
# import re
# from urllib.parse import urlparse, parse_qs
# import scrapy
# from bs4 import BeautifulSoup
#
#
# class ProxySpider(scrapy.Spider):
#     """www.xicidaili.com 高匿代理池."""
#     name = "proxy_spider"
#     start_url = 'http://www.xicidaili.com/nn/'
#
#     def start_requests(self):
#         for i in range(100):
#             yield scrapy.Request(self.start_url + str(i), callback=self.parse)
#
#     def parse(self, response):
#         soup = BeautifulSoup(response.text, 'lxml')
#
#         for tr_node in soup.find_all('tr', class_=True):
#             for th in tr_node.children:
#                 if th.string != None and len(th.string.strip()) > 0:
#                     proxy.proxy[proxy.proxyName[i]] = th.string.strip()
#                     print  'proxy',th.string.strip()
#
#
#     def validate(self, response):
#         soup = BeautifulSoup(response.text, 'lxml')
#         content = soup.find(id='ContentBody')
#         # 访问全文
#         if content.find(class_='pagesize') is not None:
#             url = response.request.url.replace('.html', '_0.html')
#             yield response.follow(url, callback=self.parse_news, meta=response.meta)
#         else:
#             item = NewsItem()
#             item['title'] = re.sub(r'</?em>', '', response.meta['title'])
#             item['time'] = response.meta['time']
#             item['company'] = response.meta['company']
#             item['url'] = response.request.url
#             item['content'] = content.get_text(strip=True)
#             yield item
