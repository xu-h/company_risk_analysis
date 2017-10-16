# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    title = scrapy.Field()
    time = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    type = scrapy.Field()
    company = scrapy.Field()


class CompanyItem(scrapy.Item):
    company = scrapy.Field()
    industry = scrapy.Field()
