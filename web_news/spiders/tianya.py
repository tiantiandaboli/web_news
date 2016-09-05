# -*- coding: utf-8 -*-
from urlparse import urljoin

import re
from scrapy import Request
from scrapy.loader import ItemLoader

from web_news.items import FroumItem
from web_news.misc.forum import SpiderForum

import time

class TianyaSpider(SpiderForum):
    name = "tianya"
    allowed_domains = ["bbs.tianya.cn"]
    website = u'天涯论坛'
    start_urls = (
        'http://bbs.tianya.cn/m/block.jsp',
    )
    def parse(self, response):
        sub_node = response.xpath('//a[re:test(@href, "list")]/@href').extract()
        return [Request(url=i, callback=self._parse_each_node) for i in sub_node]

    def parse_each_node(self, response):
        self.logger.info(response.url)

    def parse_each_item(self, response):
        pass

    def next_page(self, response):
        pass