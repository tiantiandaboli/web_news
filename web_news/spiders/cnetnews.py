# -*- coding: utf-8 -*-
import scrapy
import time
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from web_news.items import SpiderItem
from web_news.misc.spiderredis import SpiderRedis


class CnetnewsSpider(SpiderRedis):
    name = 'cnetnews'
    allowed_domains = ['cnetnews.com.cn']
    start_urls = ['http://www.cnetnews.com.cn/']

    rules = (
        Rule(LinkExtractor(allow=r'\d+/\d+/\d+\.shtml'), callback='parse_item', follow=False),
        Rule(LinkExtractor(allow=r'list'), follow=True),

    )

    def parse_item(self, response):
        l = ItemLoader(item=SpiderItem(), response=response)
        try:
            l.add_value('title', response.xpath('//h1[@class="foucs_title"]/text()').extract_first())
            date = response.xpath('//div[@class="qu_zuo"]/descendant-or-self::text()').re_first(u'\d+年\d+月\d+日')
            date = date.replace(u'年', '-').replace(u'月', '-').replace(u'日', '')
            date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.mktime(time.strptime(date, '%Y-%m-%d'))))
            l.add_value('date', date)
            l.add_value('source', 'CNET科技资讯网')
            l.add_value('content', ''.join(response.xpath('//div[@class="qu_ocn"]/descendant-or-self::text()').extract()))
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
