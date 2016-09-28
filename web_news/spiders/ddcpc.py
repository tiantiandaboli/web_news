# -*- coding: utf-8 -*-
from scrapy.spiders import Rule
from web_news.misc.spiderredis import SpiderRedis
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.items import *


class Ddcpc(SpiderRedis):
    name = "ddcpc"
    website = u"当代先锋网"
    allowed_domains = ['ddcpc.cn']
    start_urls = ['http://www.ddcpc.cn/']

    rules = [
        Rule(LinkExtractor(allow=("jr_", "gz_", "rs_", "xf_", "xcb_",
                                  "a=show&catid=(561|562|563|564|565|567|569|572|)")),
             callback="get_news", follow=False),
        Rule(LinkExtractor(allow=("/zx/", "/dj/", "/zx/rs/" "/pl/xf/", "/zx/xcb/",
                                  "a=lists&catid=(561|562|563|564|565|567|569|572|)")),
             follow=True),
    ]

    def get_news(self, response):
        try:
            loader = ItemLoader(item=SpiderItem(), response=response)

            loader.add_value('title', response.xpath('//div[@class="title"]/h2/text()').extract_first())

            date = ''.join(response.xpath('//div[@class="auther-from"]/text()').extract())
            loader.add_value('date', date[-19:])

            loader.add_value('content',
                             ''.join(response.xpath('//div[@class="content"]/descendant-or-self::text()').extract()))

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