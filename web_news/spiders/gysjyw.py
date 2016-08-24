# -*- coding: utf-8 -*-
from scrapy.spiders import Rule
from web_news.misc.spiderredis import SpiderRedis
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.items import *


class Gysjyw(SpiderRedis):
    name = "gysjyw"
    website = u"贵阳教育信息网"
    allowed_domains = ['gysjyw.gov.cn']
    start_urls = ['http://www.gysjyw.gov.cn/']

    rules = [
        Rule(LinkExtractor(allow=("/content/",)), callback="get_news", follow=False),
        Rule(LinkExtractor(allow=("/pd_",)), follow=True),
    ]

    def get_news(self, response):
        try:
            loader = ItemLoader(item=SpiderItem(), response=response)

            loader.add_value('title', response.xpath('//div[@class="article"]/h1/text()').extract_first())

            loader.add_value('date', response.xpath('//p[@class="srouce"]/text()').extract_first().strip() + ":00")

            loader.add_value('content',
                             ''.join(response.xpath('//div[@id="fz-article"]/descendant-or-self::text()').extract()))

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