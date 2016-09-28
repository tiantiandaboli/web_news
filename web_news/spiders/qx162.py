# -*- coding: utf-8 -*-
from scrapy.spiders import Rule
from web_news.misc.spiderredis import SpiderRedis
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.items import *


class Qx162(SpiderRedis):
    name = "qx162"
    website = u"黔讯网"
    allowed_domains = ['qx162.com']
    start_urls = ['http://qx162.com/']

    rules = [
        Rule(LinkExtractor(allow=("/\d+?\.shtml",)), callback="get_news", follow=True),
        Rule(LinkExtractor(allow=("news\.qx162\.com", "house\.qx162\.com", "tech\.qx162\.com")), follow=True),
    ]

    def get_news(self, response):
        try:
            loader = ItemLoader(item=SpiderItem(), response=response)

            loader.add_value('title', response.xpath('//div[@class="left"]/h1/text()').extract_first())
            loader.add_value('title', response.xpath('//h1[@class="h1"]/text()').extract_first())

            loader.add_value('date', response.xpath('//div[@class="zuoze"]/text()').extract_first())
            loader.add_value('date', response.xpath('//span[@class="post-time"]/text()').extract_first())
            date = ''.join(loader.get_collected_values('date'))
            if date == '':
                return
            loader.replace_value('date', date.strip() + ":00")

            loader.add_value('content',
                             ''.join(response.xpath('//span[@id="zoom"]/descendant-or-self::text()').extract()))
            loader.add_value('content',
                             ''.join(response.xpath('//p[@class="summary"]/descendant-or-self::text()').extract()))

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