# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.http import Request, HtmlResponse

from web_news.items import *
from web_news.misc.filter import Filter
import time


class CpcnewsSpider(CrawlSpider):
    name = 'cpcnews'
    website = u'中共共产党新闻网'
    allowed_domains = ['people.com.cn']
    start_urls = ['http://cpc.people.com.cn/']

    rules = [
        Rule(LinkExtractor(allow=("cpc.people.com.cn/n1/",
                                  "dangjian.people.com.cn/n1/",
                                  "fanfu.people.com.cn/n1/",
                                  "theory.people.com.cn/n1/",
                                  "renshi.people.com.cn/n1/",)), callback="get_news", follow=True),
        Rule(
            LinkExtractor(allow=("cpc.people.com.cn/GB/",
                                 "dangjian.people.com.cn/GB/",
                                 "fanfu.people.com.cn/GB/",
                                 "theory.people.com.cn/GB/",
                                 "renshi.people.com.cn/GB/")), follow=True),
    ]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(CpcnewsSpider, cls).from_crawler(crawler, *args, **kwargs)
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

    def get_news(self, response):
        try:
            loader = ItemLoader(item=SpiderItem(), response=response)

            loader.add_value('title', response.xpath('//div[@class="text"]/h1/text()').extract_first())
            loader.add_value('title', response.xpath('//div[@class="text_c clearfix"]/h1/text()').extract_first())
            loader.add_value('title', response.xpath('//div[@class="text_c"]/h1/text()').extract_first())
            loader.add_value('title', response.xpath('//div[@class="d2_left wb_left fl"]/h1/text()').extract_first())

            loader.add_value('date', response.xpath('//p[@class="text_tools"]/text()').extract_first())
            loader.add_value('date', response.xpath('////div[@class="text_c clearfix"]/h5/text()').extract_first())
            loader.add_value('date', response.xpath('//p[@class="sou"]/text()').extract_first())
            loader.add_value('date', response.xpath('//span[@id="p_publishtime"]/text()').extract_first())
            date = ''.join(loader.get_collected_values('date'))
            date = time.strptime(date.split()[0], u'%Y年%m月%d日%H:%M')
            loader.replace_value('date', time.strftime('%Y-%m-%d %H:%M:%S', date))

            loader.add_value('content', ''.join(response.xpath('//div[@class="text_c"]/descendant-or-self::text()').extract()))
            loader.add_value('content', ''.join(response.xpath('//div[@class="text_show"]/descendant-or-self::text()').extract()))
            loader.add_value('content', ''.join(response.xpath('//div[@class="show_text"]/descendant-or-self::text()').extract()))
            loader.add_value('content', ''.join(response.xpath('//div[@id="p_content"]/descendant-or-self::text()').extract()))

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
