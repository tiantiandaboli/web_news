from scrapy.spiders import Spider
from scrapy.http import FormRequest, Request
import json
import time
from web_news.items import SpiderItem


class NewsSpider(Spider):
    name = 'web12371'
    allowed_domains = ['12371.cn']
    start_urls = ['http://news.12371.cn/qwfb/']

    def parse(self, response):
        for sel in response.xpath('//div[@class="gcdywB4994_ind02"]/p'):
            url = sel.xpath('a/@href').extract()[0]
            headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
                'Host': "news.12371.cn",
                'Referer': url
            }
            date = time.strftime('%Y%m%d', time.localtime())
            url += 'data/' + date + '.shtml?t=' + str(int(time.time()*1000))
            yield FormRequest(url=url, headers=headers, method="GET", meta={
                'dont_redirect': True, 'handle_httpstatus_list': [302]}, callback=self.get_news_list)

    def get_news_list(self, response):
        msg = json.loads(response.body_as_unicode())['rollData']
        for result in msg:
            item = SpiderItem()
            item['title'] = result['title']
            item['date'] = result['dateTime']
            item['brief'] = result['brief']
            item['url'] = result['url']
            request = Request(result['url'], callback=self.get_news)
            request.meta['item'] = item
            yield request

    def get_news(self, response):
        data = response.xpath('//div[@id="font_area"]')
        content = data.xpath('string(.)').extract()[0]
        item = response.meta['item']
        item['content'] = content
        item['collection_name'] = self.name
        yield item