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
        base_url = 'http://bbs.tianya.cn'
        for i in xrange(len(sub_node)):
            if not sub_node[i].startswith('http'):
                sub_node[i] = base_url+sub_node[i]

        return [Request(url=i, callback=self._parse_each_node) for i in sub_node]

    def parse_each_node(self, response):
        # self.logger.info(response.url)
        base_url = 'http://bbs.tianya.cn'
        posts = [Request(url=base_url+i) for i in response.xpath('//ul[@class="post-list"]/li/a[re:test(@href, "post")]/@href').extract()]
        return posts

    def parse_each_item(self, response):
        self.logger.debug(response.url)

    def next_page(self, response):
        pass