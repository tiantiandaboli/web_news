# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from scrapy.loader import ItemLoader
from scrapy.http import Request, HtmlResponse

from web_news.items import SpiderItem
from web_news.misc.filter import Filter

from scrapy.shell import  inspect_response

class BjnewsSpider(CrawlSpider):
    name = 'bjnews'
    website = u'新京报网'
    allowed_domains = ['www.bjnews.com.cn']
    start_urls = ['http://www.bjnews.com.cn/news/']

    rules = (
        Rule(LinkExtractor(allow=r'news/(\d+){4}/(\d+){2}/(\d+){2}/(\d+)'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'news/list-43-page-(\d+)'), follow=True),
        Rule(LinkExtractor(allow=r'news/?page=(\d+)'), follow=True),
    )

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BjnewsSpider, cls).from_crawler(crawler, *args, **kwargs)
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
        l = ItemLoader(item=SpiderItem(), response=response)
        inspect_response(response, self);
        try:

            pass
        except Exception as e:

            pass
        finally:
            return l.load_item()
            pass

