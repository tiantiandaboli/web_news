# -*- coding: utf-8 -*-
from scrapy.spiders import Rule
from web_news.misc.spiderredis import SpiderRedis
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.misc.filter import Filter
from web_news.items import *


class Swjw(SpiderRedis):
    name = "swjw"
    website = "贵阳市卫生和计划委员会"
    allowed_domains = ['swjw.gygov.gov.cn']
    start_urls = ['http://swjw.gygov.gov.cn']

    rules = [
        Rule(LinkExtractor(allow=("/art/",)), callback="get_news", follow=True),
        Rule(LinkExtractor(allow=("/col/",)), follow=True),
    ]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(Swjw, cls).from_crawler(crawler, *args, **kwargs)
        spider.filter = Filter.from_crawler(spider.crawler, spider.name)
        return spider

    def get_news(self, response):
        try:
            loader = ItemLoader(item=SpiderItem(), response=response)

            loader.add_value('title', response.xpath('//table[@width="90%"]/tr/td/text()').extract_first())

            date = response.xpath('//table[@width="90%"]/tr/td/text()').extract()[1][-10:]
            loader.add_value('date', date.strip() + " 00:00:00")

            loader.add_value('content',
                             ''.join(response.xpath('//div[@id="zoom"]/descendant-or-self::text()').extract()))

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