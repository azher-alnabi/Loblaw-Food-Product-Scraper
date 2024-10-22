import scrapy
from scrapy_playwright.page import PageMethod
import json
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class StoreSpider(scrapy.Spider):
    name = "food"
    allowed_domains = ["zehrs.ca"]
    start_page_number = 1

    with open('initalization.json', 'r') as file:
        end_page = json.load(file)

    end_page_number = int(end_page[0]['end_page_number'])


    def start_requests(self):
        while self.start_page_number <= self.end_page_number:
            yield scrapy.Request(
                url = f"https://www.zehrs.ca/food/c/27985?page={self.start_page_number}",
                meta = {
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", '.css-1rb8z0p', timeout=60000),
                        PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                    ],
                },
                callback=self.parse,
            )
            print(f"\nScraping page {self.start_page_number}\n")
            self.start_page_number += 1


    async def parse(self, response):

        if response.css('p[data-testid="sub-heading"]::text').get() == "No items are available":
            pass

        else:
            for food in response.css("div.css-0"):
                yield {
                    "product-discription": {
                        "product-brand": food.css('p[data-testid="product-brand"]::text').get(),
                        "title": food.css('h3[data-testid="product-title"]::text').get(),
                        "package-size": food.css('p[data-testid="product-package-size"]::text').get(),
                        "image_url": food.css('div[data-testid="product-image"] img::attr(src)').get(),
                    },
                    "price-list": {
                        "regular-price": food.css('span[data-testid="regular-price"]::text').get(),
                        "sale-price": food.css('span[data-testid="sale-price"]::text').get(),
                        "non-member-price": food.css('span[data-testid="non-member-price"]::text').get(),
                        "former-price": food.css('span[data-testid="was-price"]::text').get(),
                    },
                }


process = CrawlerProcess(settings = get_project_settings())
process.crawl(StoreSpider)
process.start()