# -*- coding: utf-8 -*-
from scrapy.spiders import Rule
from web_news.misc.spiderredis import SpiderRedis
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request, HtmlResponse
from scrapy.loader import ItemLoader
from web_news.misc.filter import Filter
from web_news.items import *
import time


class Gyasc(SpiderRedis):
    name = "gyasc"
    website = u"贵阳市人民政府政务服务中心"
    allowed_domains = ['gyasc.gov.cn']
    start_urls = ['http://www.gyasc.gov.cn/']

    rules = [
        Rule(LinkExtractor(allow=("/\d+?\.jhtml",)), callback="get_news", follow=True),
        Rule(LinkExtractor(allow=("index",)), follow=True),
    ]

    def get_news(self, response):
        try:
            loader = ItemLoader(item=SpiderItem(), response=response)

            loader.add_value('title', response.xpath('//div[@class="ztzlxxbt"]/text()').extract_first())

            date = response.xpath('//div[@class="ztzlxxbt1"]/text()').extract_first()
            loader.add_value('date', date[date.find(u'发布时间：')+5:][:10] + " 00:00:00")

            loader.add_value('content',
                             ''.join(response.xpath('//div[@class="ztzlxxtu"]/descendant-or-self::text()').extract()))

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