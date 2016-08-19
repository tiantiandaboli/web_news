# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from web_news.misc.spiderredis import SpiderRedis

class HuanqiuSpider(SpiderRedis):
    name = 'huanqiu'
    allowed_domains = ['china.huanqiu.com', 'society.huanqiu.com']
    start_urls = ['http://www.huanqiu.com/']
    website = u'环球网'

    rules = (
        Rule(LinkExtractor(allow=r'article/.*/(\d+).ht'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'society.huanqiu.com'), follow=True),
        Rule(LinkExtractor(allow=r'china.huanqiu.com'), follow=True),
    )

    def parse_item(self, response):
        i = {}
        i['title'] = response.xpath('//title/text()').extract_first()
        try:
            if response.status != 200:
                raise Exception('response status %s'%response.status)
            i['date'] = response.xpath('//strong[@id="pubtime_baidu"]/text()').extract_first()
            i['source'] = response.xpath('//strong[@id="source_baidu"]/text()').extract_first()
            i['content'] = ''.join(response.xpath('//div[@class="text"]/descendant-or-self::text()').extract())
            # found new fomate
            assert i['date'] != '';
            assert i['source'] != '';
            assert i['content'] != '';

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