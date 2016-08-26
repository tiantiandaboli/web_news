# -*- coding: utf-8 -*-
from urlparse import urljoin

from scrapy import Request
from scrapy.loader import ItemLoader

from web_news.items import FroumItem
from web_news.misc.forum import SpiderForum


class TongrenSpider(SpiderForum):
    name = "tongren"
    allowed_domains = ["www.daguizx.com"]
    website = u'铜仁论坛'
    start_urls = (
        'http://www.daguizx.com/tongren/',
    )

    def parse_each_node(self, response):
        tbody_list = response.xpath('//tbody[re:test(@id, "normalthread_\d+")]')
        for i, tbody in enumerate(tbody_list):
            url = tbody.xpath('descendant::td[@class="num"]/a/@href').extract_first()
            yield Request(url=urljoin(response.request.url, url))

    def parse_each_item(self, response):
        if response.meta.get('iteminfo') == None:
            iteminfo = {}
            iteminfo['url'] = response.url
            iteminfo['view_num'] = response.xpath('//div[@class="hm ptn"]/span[2]/text()').extract_first()
            iteminfo['reply_num'] = response.xpath('//div[@class="hm ptn"]/span[5]/text()').extract_first()
            iteminfo['title'] = response.xpath('//span[@id="thread_subject"]/text()').extract_first()
            iteminfo['content'] = ''.join(response.xpath('//td[re:test(@id, "postmessage_\d+")]')[0].xpath('text()').extract())
            iteminfo['collection_name'] = self.name
            iteminfo['website'] = self.website
            iteminfo['date'] = response.xpath('//em[re:test(@id, "authorposton\d+")]')[0].xpath('text()').re_first('\d+-\d+-\d+\W\d+:\d+:\d+') \
                               or response.xpath('//em[re:test(@id, "authorposton\d+")]')[0].xpath('span/@title').re_first('\d+-\d+-\d+\W\d+:\d+:\d+')
            yield Request(url=response.request.url+'?page=100000000', callback=self.parse_each_item, meta={'iteminfo':iteminfo})
        else:
            iteminfo = response.meta.get('iteminfo')
            iteminfo['last_reply'] = response.xpath('//em[re:test(@id, "authorposton\d+")]')[-1].xpath('text()').re_first('\d+-\d+-\d+\W\d+:\d+:\d+') \
                                     or response.xpath('//em[re:test(@id, "authorposton\d+")]')[-1].xpath('span/@title').re_first('\d+-\d+-\d+\W\d+:\d+:\d+')
            item = ItemLoader(item=FroumItem(), response=response)
            for k, v in iteminfo.items():
                item.add_value(k, v)
            yield item.load_item()

    def next_page(self, response):
        pass