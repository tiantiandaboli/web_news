# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from web_news.misc.spiderredis import SpiderRedis
from web_news.items import SpiderItem
from  scrapy.loader import ItemLoader
from  urlparse import urljoin
import re
from datetime import datetime, timedelta

class SznewsSpider(SpiderRedis):
    name = 'sznews'
    allowed_domains = ['jb.sznews.com']
    start_urls = ['http://jb.sznews.com/']
    website = u'晶报网'

    rules = (
        Rule(LinkExtractor(allow=r'content_'), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=r'node_'), follow=True),
        # main page dynamic load today news
        # Rule(LinkExtractor(allow=r'jb.sznews.com'), callback="main_page", follow=True),
    )
    def parse_start_url(self, response):
        url = urljoin(response.url, re.search(r'html/.*/node_1163.htm', response.body).group())
        # request real news url
        yield scrapy.Request(url=url, callback=self._requests_to_follow)
        a = re.search(r'\d+-\d+/\d+', url).group().replace('-', '/').split('/')
        today = datetime(year=int(a[0]), month=int(a[1]), day=int(a[2]))
        delta = timedelta(days=1)
        yestoday = today-delta
        yesurl = 'html/%s-%s/%s/node_1163.htm'%(yestoday.year, yestoday.month, yestoday.day)
        # try request yestodays news
        yield scrapy.Request(url=urljoin(response.url, yesurl), callback=self.old_news)

    def old_news(self, response):
        if response.status == 404:
            return
        # parse today news
        self._requests_to_follow(response)
        links = self.filter.bool_fllow(response, self.rules)
        if len(links) > 0:
            # if found some url not exist in db, check yestoday's news
            a = re.search(r'\d+-\d+/\d+', response.url).group().replace('-', '/').split('/')
            today = datetime(year=int(a[0]), month=int(a[1]), day=int(a[2]))
            delta = timedelta(days=1)
            yestoday = today - delta
            yesurl = 'html/%s-%s/%s/node_1163.htm' % (yestoday.year, yestoday.month, yestoday.day)
            yield scrapy.Request(url=urljoin(response.url, yesurl), callback=self.old_news)
        else:
            return


    def parse_item(self, response):
        l = ItemLoader(item=SpiderItem(), response=response)
        try:
            if re.search(r'/404.h', response.body) != None:
                raise Exception('this item may be deleted')
            if response.status != 200:
                raise Exception('response status %s'%response.status)
            l.add_value('title', response.xpath('//title/text()').extract_first() or '')
            date = response.xpath('//td[@width="25%"]/text()').re(u"\d+年\d+月\d+日")[0]
            date.replace(u'年', '-').replace(u'月', '-').replace(u'日', '-')
            l.add_value('date', date)
            l.add_value('source', self.website)
            l.add_value('content', ''.join(response.xpath('//div[@id="ozoom"]/descendant-or-self::p/text()').extract()) or '')

        except Exception as e:
            self.logger.error('error url: %s error msg: %s' % (response.url, e))
            l = ItemLoader(item=SpiderItem(), response=response)
            l.add_value('title', '')
            l.add_value('date', '1970-01-01 00:00:00')
            l.add_value('source', '')
            l.add_value('content', '')
        finally:
            l.add_value('url', response.url)
            l.add_value('collection_name', self.name)
            l.add_value('website', self.website)
            return l.load_item()