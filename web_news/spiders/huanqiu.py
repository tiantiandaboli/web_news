# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from web_news.misc.spiderredis import SpiderRedis
import re

class HuanqiuSpider(SpiderRedis):
    name = 'huanqiu'
    allowed_domains = ['china.huanqiu.com', 'society.huanqiu.com']
    start_urls = ['http://china.huanqiu.com/article/2016-08/9318559.html']
    website = u'环球网'

    rules = (
        Rule(LinkExtractor(allow=r'article/.*/(\d+)(_\d+){0,1}.ht'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'society.huanqiu.com'), follow=True),
        Rule(LinkExtractor(allow=r'china.huanqiu.com'), follow=True),
    )

    def parse_item(self, response):
        i = {}
        i['title'] = response.xpath('//title/text()').extract_first()
        try:
            if response.url == 'http://www.huanqiu.com' or re.search(r'/404.h', response.body) != None:
                raise Exception('this item may be deleted')
            if response.status != 200:
                raise Exception('response status %s'%response.status)
            i['date'] = response.xpath('//strong[@id="pubtime_baidu"]/descendant-or-self::text()').extract_first()
            i['source'] = response.xpath('//strong[@id="source_baidu"]/descendant-or-self::text()').extract_first()
            i['content'] = ''.join(response.xpath('//div[@class="text"]/descendant-or-self::text()').extract())
            # found new fomate
            assert i['date'] != '', 'date not found'
            assert i['source'] != '', 'source not found'
            assert i['content'] != '', 'content not found'
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            i['date'] = '1970-01-01 00:00:00'
            i['source'] = ''
            i['content'] = ''
        finally:
            i['url'] = response.url
            i['collection_name'] = self.name
            i['website'] = self.website
        return i