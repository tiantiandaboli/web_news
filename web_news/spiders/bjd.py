# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from web_news.misc.spiderredis import SpiderRedis
from web_news.items import SpiderItem
from scrapy.loader import ItemLoader

class BjdSpider(SpiderRedis):
    name = 'bjd'
    allowed_domains = ['www.bjd.com.cn']
    start_urls = ['http://www.bjd.com.cn/']
    website = u'京报网'

    rules = (
        Rule(LinkExtractor(allow=r't(\d+)_(\d+)'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'bjd.com.cn'), follow=True),
    )

    def parse_item(self, response):
        i = {}
        i['title'] = response.xpath('//title/text()').extract_first()
        try:
            date_source_author = response.xpath('//div[@class="info"]/span/text()').extract()
            i['date'] = date_source_author[0] if len(date_source_author)>0 else '1970-01-01 00:00:00'
            i['source'] = date_source_author[1] if len(date_source_author)>1 else ''
            i['content'] = ''.join(response.xpath('//div[@class="TRS_Editor"]/descendant-or-self::text()').extract())
        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            i['date'] = '1970-01-01 00:00:00'
            i['source'] = ''
            i['content'] = ''
        finally:
            i['url'] = response.url
            i['collection_name'] = self.name
            i['website'] = self.website
        l = ItemLoader(item=SpiderItem(), response=response)
        for k, v in i.items():
            l.add_value(k, v)
        return l.load_item()