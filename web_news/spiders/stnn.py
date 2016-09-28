# -*- coding: utf-8 -*-
from scrapy.spiders import Rule
from web_news.misc.spiderredis import SpiderRedis
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from web_news.items import *


class Stnn(SpiderRedis):
    name = "stnn"
    website = u"星球环岛网"
    allowed_domains = ['stnn.cc']
    start_urls = ['http://www.stnn.cc/']

    rules = [
        Rule(LinkExtractor(allow=("/\d+?\.shtml$",),
                           deny=("tu\.stnn\.cc", "video\.stnn\.cc", "history\.stnn\.cc", "oversea\.stnn\.cc")),
             callback="get_news", follow=True),
        Rule(LinkExtractor(allow=("news\.stnn\.cc/[A-Za-z_]+?/$", "finance\.stnn\.cc/[A-Za-z_]+?/$",
                                  "feature\.stnn\.cc/[A-Za-z_]+?/$"),
                           deny=("news\.stnn\.cc/rdwtdztp/",)),
             follow=True)
    ]

    def get_news(self, response):
        try:
            loader = ItemLoader(item=SpiderItem(), response=response)

            loader.add_value('title', response.xpath('//h1[@class="article-title"]/text()').extract_first())

            loader.add_value('date', response.xpath('//span[@class="date"]/text()').extract_first() + ":00")

            loader.add_value('content', ''.join(response.xpath(
                '//div[@class="article-content fontSizeSmall BSHARE_POP"]/descendant-or-self::text()').extract()))

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