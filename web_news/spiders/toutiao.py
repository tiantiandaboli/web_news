# -*- coding: utf-8 -*-
from web_news.misc.spiderredis import SpiderRedis
from scrapy.http import Request
from scrapy.loader import ItemLoader
import time
import json
from web_news.items import *


class Toutiao(SpiderRedis):
    name = "toutiao"
    website = "今日头条"
    allowed_domains = ['toutiao.com']

    def start_requests(self):
        get_url = "http://toutiao.com/api/article/recent/?source=2&as=A10517AB7ABF72F&cp=57BA2F27B2EF3E1"
        categorys = ["news_society", "news_tech", "news_military", "news_world", "news_finance"]
        for category in categorys:
            timestamp = int(time.mktime(time.localtime()))
            yield Request(url=get_url + '&category=' + category + '&_=' + str(timestamp), callback=self.parse)

    def parse(self, response):
        data = json.loads(response.body_as_unicode())
        next_page = data['next']['max_behot_time']
        category = data['data'][0]['tag']
        for data in data['data']:
            if not data['has_video'] and data['article_genre'] == 'article':
                yield Request(url="http://toutiao.com" + data['source_url'], callback=self.parse_item)
        get_url = "http://toutiao.com/api/article/recent/?source=2&as=A10517AB7ABF72F&cp=57BA2F27B2EF3E1"
        yield Request(url=get_url + '&category=' + category + '&_=' + str(next_page), callback=self.parse)

    def parse_item(self, response):
        if response.url.find('toutiao.com') > 0 and response.url.find('?_as_') == -1:
            loader = ItemLoader(item=SpiderItem(), response=response)

            loader.add_value('title', response.xpath('//h1[@class="title"]/text()').extract())

            loader.add_value('date', response.xpath('//span[@class="time"]/text()').extract_first() + ":00")

            loader.add_value('content', ''.join(
                response.xpath('//div[@class="article-content"]/descendant-or-self::text()').extract()))

            loader.add_value('url', response.url)
            loader.add_value('collection_name', self.name)
            loader.add_value('website', self.website)

            yield loader.load_item()