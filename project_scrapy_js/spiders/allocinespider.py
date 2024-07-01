import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import FilmItem

class AllocinespiderSpider(CrawlSpider):
    name = 'allocinespider'
    allowed_domains = ["allocine.fr"]
    start_urls = ["https://www.allocine.fr/film/meilleurs"]

    rules = (
        Rule(LinkExtractor(restrict_xpaths="//h2/a"), callback='parse_item', follow=False),
        Rule(LinkExtractor(restrict_xpaths="//span[@class='txt' and text()='Suivante']/.."), follow=True, process_request='use_playwright'),
    )

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, meta={"playwright": True})

    def use_playwright(self, request):
        request.meta.update({"playwright": True})
        return request

    def parse_item(self, response):
        item = FilmItem()
        item['title'] = response.xpath("//div[@class='titlebar-title titlebar-title-xl']/text()").get()
        yield item


