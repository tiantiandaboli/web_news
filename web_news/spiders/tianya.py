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

        # return [Request(url=i, callback=self._parse_each_node) for i in sub_node]
        return Request(url='http://bbs.tianya.cn/m/list-free-1.shtml', callback=self._parse_each_node)

    def parse_each_node(self, response):
        # self.logger.info(response.url)
        base_url = 'http://bbs.tianya.cn'
        posts = [Request(url=base_url+i) for i in response.xpath('//ul[@class="post-list"]/li/a[re:test(@href, "post")]/@href').extract()]
        return posts

    def parse_each_item(self, response):
        # self.logger.debug(response.url)
        ret = None
        if response.meta.get('iteminfo') == None:
            iteminfo = {}
            iteminfo['url'] = response.url
            iteminfo['view_num'] = response.xpath('//i[@class="iconfont icon-view"]/text()').extract_first().strip()
            iteminfo['reply_num'] = response.xpath('//i[@class="iconfont icon-reply"]/text()').extract_first().strip()
            iteminfo['title'] = response.xpath('//h1/text()').extract_first()
            try:
                iteminfo['content'] = ''.join(response.xpath('//div[@class="bd"]')[0].xpath('descendant-or-self::text()').extract())
            except Exception as e:
                iteminfo['content'] = ''

            iteminfo['collection_name'] = self.name
            iteminfo['website'] = self.website
            iteminfo['date'] = response.xpath('//p[@class="time fc-gray"]/text()')[0].extract()
            # yield Request(url=response.request.url+'?page=100000000', callback=self.parse_each_item, meta={'iteminfo':iteminfo})
            last_page = 'http://bbs.tianya.cn/m/post-free-5573164-9999999.shtml'
            url = re.sub('-\d+-', re.search(r'-\d+-', response.url).group(), last_page)
            ret = Request(url=url, meta={'iteminfo':iteminfo})
        else:
            iteminfo = response.meta.get('iteminfo')
            iteminfo['last_reply'] = iteminfo['date'] = response.xpath('//p[@class="time fc-gray"]/text()')[-1].extract()
            item = ItemLoader(item=FroumItem(), response=response)
            for k, v in iteminfo.items():
                item.add_value(k, v)
            ret = item.load_item()
        return ret

    def next_page(self, response):
        next_pg = response.xpath('//a[@class="u-btn "]/@href').re_first('/m/list\.jsp\?item=free\&nextid=\d+')
        base_url = 'http://bbs.tianya.cn'
        return Request(url=urljoin(base_url, next_pg)) if next_pg else None