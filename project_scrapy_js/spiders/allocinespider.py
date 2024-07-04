import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import FilmItem

class AllocinespiderSpider(CrawlSpider):
    name = 'allocinespider'
    allowed_domains = ["allocine.fr"]
    start_urls = ["https://www.allocine.fr/film/meilleurs"]

    rules = (
        Rule(LinkExtractor(restrict_xpaths="//h2/a"), callback='parse_item', follow=False, process_request='use_playwright'),
        Rule(LinkExtractor(restrict_xpaths="//span[@class='txt' and text()='Suivante']/.."), follow=True, process_request='use_playwright'),
    )

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, meta={"playwright": True})

    def use_playwright(self, request, response):
        request.meta.update({"playwright": True})
        return request


    def parse_item(self, response):
        item = FilmItem()
        item['title'] = response.xpath("//div[@class='titlebar-title titlebar-title-xl']/text()").get()
        item["titre_original"] = response.xpath("//div[@class='meta-body-item']/span[@class='dark-grey']/text()").get()
        if not item["titre_original"]:
            item["titre_original"] = item['title']
        item["genre"] = response.xpath("//div[@class='meta-body-item meta-body-info']/a[contains(@href, 'genre')]/text()").getall()
        item["duree"] = ''.join(response.xpath("//div[@class='meta-body-item meta-body-info']/text()").getall()).replace(',','').strip()
        item["description"] = response.xpath("//p[@class='bo-p']/text()").get()
        item["acteurs"] = response.xpath("//div/span[contains(text(), 'Avec')]/../a/text()").getall()
        item["realisateur"] = response.xpath("//div/span[contains(text(), 'De')]/../a/text()").getall()
        item["public"] = response.xpath("//div[@class='certificate']/span[@class='certificate-text']/text()").get()
        item["pays"] = response.xpath("//a[@class='xXx nationality']/text()").get()
        item["url_image"] = response.xpath("//div[@class='card entity-card entity-card-list cf entity-card-player-ovw']/figure/a/img/@src").get()
        item["langues"] = response.xpath("//div[@class='item']/span[contains(text(), 'Langues')]/following-sibling::span/text()").get().strip()

        item["score"] = response.xpath("//a[contains(text(), ' Spectateurs ')]/../div/span[@class='stareval-note']/text()").get()
        meta = response.meta.copy()
        meta.update({"playwright": False, "item": item})
        yield scrapy.Request(response.url, callback=self.parse_item_no_js, meta=meta, dont_filter=True)

    def parse_item_no_js(self,response):
        item = response.meta['item']
        item["date"] = response.xpath("//span[contains(@class, '== date blue-link')]/text()").get().strip()
        yield item


