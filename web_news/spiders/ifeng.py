# -*- coding: utf-8 -*-
import re

import scrapy
import time
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from web_news.items import SpiderItem
from web_news.misc.spiderredis import SpiderRedis


class IfengSpider(SpiderRedis):
    name = 'ifeng'
    allowed_domains = ['news.ifeng.com', 'tech.ifeng.com', 'finance.ifeng.com']
    start_urls = [ 'http://www.ifeng.com/']
    website = u'凤凰网'

    rules = (
        Rule(LinkExtractor(allow=r'\d{8}/\d+_\d+.shtml'), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=r'ifeng'), follow=True),
    )

    def parse_item(self, response):
        l = ItemLoader(item=SpiderItem(), response=response)
        try:
            title = response.xpath('//h1[@id="artical_topic"]/text()').extract_first()
            if title == None:
                self.logger.info("title is null, url:%s"%response.url)
            l.add_value('title', title)
            date = response.xpath('//span[@itemprop="datePublished"]/text()').extract_first()
            if date == None:
                self.logger.info("date is null, url:%s"%response.url)
            date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.mktime(time.strptime(date, u'%Y年%m月%d日 %H:%M'))))
            l.add_value('date', date)
            classname = ['main_content']
            content = ''
            for c in classname:
                content += ''.join(response.xpath('//div[@id="%s"]/descendant-or-self::text()'%c).extract())
            if content == None or content.strip() == '':
                self.logger.info("content is null, url:%s"%response.url)
            l.add_value('content', content)
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            l = ItemLoader(item=SpiderItem(), response=response)
            l.add_value('title', '')
            l.add_value('date', '1970-01-01 00:00:00')
            l.add_value('source', '')
            l.add_value('content', '')
            pass
        finally:
            l.add_value('url', response.url)
            l.add_value('collection_name', self.name)
            l.add_value('website', self.website)
            return l.load_item()
