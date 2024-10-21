import scrapy
from scrapy_playwright.page import PageMethod
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class PaginationSpider(scrapy.Spider):
    name = "pagination"
    allowed_domains = ["zehrs.ca"]


    def start_requests(self):
        yield scrapy.Request(
            url = f"https://www.zehrs.ca/food/c/27985",
            meta = {
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", '.css-1rb8z0p', timeout=60000),
                ],
            },
        )


    def parse(self, response):
        end_page_number = response.css('a.chakra-link.css-1vwc5vj::text').getall()[-1]
        yield {
            "end_page_number": end_page_number
        }

process = CrawlerProcess (settings = get_project_settings())
process.crawl(PaginationSpider)
process.start()