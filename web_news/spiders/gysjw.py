# -*- coding: utf-8 -*-
from re import search

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request, HtmlResponse
from scrapy.loader import ItemLoader

from web_news.items import SpiderItem
from web_news.misc.filter import Filter


class GysjwSpider(CrawlSpider):
    name = 'gysjw'
    allowed_domains = ['gysjw.gov.cn']
    start_urls = ['http://www.gysjw.gov.cn/']
    website = u'中共贵阳市纪律检查委员会、贵阳市监察局'
    rules = (
        Rule(LinkExtractor(allow=r'content_'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'node_'), callback='_requests_to_follow', follow=True),
    )

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(GysjwSpider, cls).from_crawler(crawler, *args, **kwargs)
        spider.filter = Filter.from_crawler(spider.crawler, spider.name)
        return spider

    def _requests_to_follow(self, response):
        links = self.filter.bool_fllow(response, self.rules)
        if len(links) > 0:
            for link in links:
                r = Request(url=link.url, callback=self._response_downloaded)
                r.meta.update(rule=0, link_text=link.text)
                yield self.rules[0].process_request(r)
            if not isinstance(response, HtmlResponse):
                return
            seen = set()
            for n, rule in enumerate(self._rules):
                if n == 0:
                    continue
                links = [lnk for lnk in rule.link_extractor.extract_links(response)
                         if lnk not in seen]
                if links and rule.process_links:
                    links = rule.process_links(links)
                for link in links:
                    seen.add(link)
                    r = Request(url=link.url, callback=self._response_downloaded)
                    r.meta.update(rule=n, link_text=link.text)
                    yield rule.process_request(r)
        else:
            return 

    def parse_item(self, response):
        try:
            l = ItemLoader(item=SpiderItem(), response=response)
            l.add_value('title', response.xpath('//title/text()').extract_first())
            da = response.xpath('//div[@class="conpage"]/span/text()').extract_first().split(u'\xa0\xa0\xa0\xa0')
            da[1] = search(r'\d+-\d+-\d+\s+(\d+){0,1}(:\d+){0,2}', da[1]).group()
            if da[1].count(':') == 1:
                da[1] += ':00'
            l.add_value('date', da[1])
            l.add_value('source', da[0])
            l.add_value('content', ''.join(response.xpath('//div[@class="conpage"][2]/descendant-or-self::text()').extract()))
            l.add_value('url', response.url)
            l.add_value('collection_name', self.name)
            l.add_value('website', self.website)
            return l.load_item()
        except Exception as e:
            self.logger.error('error url: %s error msg: %s'%(response.url, e))
            l = ItemLoader(item=SpiderItem(), response=response)
            l.add_value('title', '')
            l.add_value('date', '1970-01-01 00:00:00')
            l.add_value('source', '')
            l.add_value('content', '')
            l.add_value('url', response.url)
            l.add_value('collection_name', self.name)
            l.add_value('website', self.website)
            return l.load_item()
