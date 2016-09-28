# -*- coding: utf-8 -*-
from scrapy.spiders import Rule
from web_news.misc.spiderredis import SpiderRedis
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request, HtmlResponse
from scrapy.loader import ItemLoader
from web_news.misc.filter import Filter
from web_news.items import *
import time


class Gygov(SpiderRedis):
    name = "gygov"
    website = u"中国贵阳"
    allowed_domains = ['gygov.gov.cn']
    start_urls = ['http://www.gygov.gov.cn/']

    rules = [
        Rule(LinkExtractor(allow=("/art/",)), callback="get_news", follow=False),
        Rule(LinkExtractor(allow=("/col/",)), follow=True),
    ]

    def get_news(self, response):
        try:
            loader = ItemLoader(item=SpiderItem(), response=response)

            loader.add_value('title', response.xpath('//td[@class="title"]/text()').extract_first())

            url = response.url
            date = url[url.find('art')+4:url.find('art_')-1]
            date = time.strptime(date, '%Y/%m/%d')
            loader.add_value('date', time.strftime('%Y-%m-%d %H:%M:%S', date))

            loader.add_value('content',
                             ''.join(response.xpath('//div[@id="zoom"]/p/descendant-or-self::text()').extract()))

            loader.add_value('url', response.url)
            loader.add_value('collection_name', self.name)
            loader.add_value('website', self.website)

            return loader.load_item()
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            l = ItemLoader(item=SpiderItem(), response=response)
            l.add_value('title', '')
            l.add_value('date', '1970-01-01 00:00:00')
            l.add_value('source', '')
            l.add_value('content', '')
            l.add_value('url', response.url)
            l.add_value('collection_name', self.name)
            l.add_value('website', self.website)
            return l.load_item()