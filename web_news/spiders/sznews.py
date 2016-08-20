# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from web_news.misc.spiderredis import SpiderRedis
from web_news.items import SpiderItem
from  scrapy.loader import ItemLoader
import re

class SznewsSpider(SpiderRedis):
    name = 'sznews'
    allowed_domains = ['jb.sznews.com']
    start_urls = ['http://jb.sznews.com/']
    website = u'晶报网'

    rules = (
        Rule(LinkExtractor(allow=r'content_'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'node_'), follow=True),
    )

    def parse_item(self, response):
        l = ItemLoader(item=SpiderItem(), response=response)
        try:
            if re.search(r'/404.h', response.body) != None:
                raise Exception('this item may be deleted')
            if response.status != 200:
                raise Exception('response status %s'%response.status)
            l.add_value('title', response.xpath('//title/text()').extract_first() or '')
            date = response.xpath('//td[@width="25%"]/text()').re(u"\d+年\d+月\d+日")[0]
            date.replace(u'年', '-').replace(u'月', '-').replace(u'日', '-')
            l.add_value('date', date)
            l.add_value('source', self.website)
            l.add_value('content', ''.join(response.xpath('//div[@id="ozoom"]/descendant-or-self::p/text()').extract()) or '')

        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            l = ItemLoader(item=SpiderItem(), response=response)
            l.add_value('title', '')
            l.add_value('date', '1970-01-01 00:00:00')
            l.add_value('source', '')
            l.add_value('content', '')
        finally:
            l.add_value('url', response.url)
            l.add_value('collection_name', self.name)
            l.add_value('website', self.website)
            return l.load_item()