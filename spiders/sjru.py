# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=логист']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@class="icMQ_ _1_Cht _3ze9n f-test-button-dalshe f-test-link-dalshe"]/@href').get()
        yield response.follow(next_page, callback=self.parse)
        vacancy = response.xpath(
            '//div[contains(@class, "f-test-vacancy-item")]//a[contains(@class, "icMQ_") and contains(@class,"_1QIBo ")]/@href' ).getall()
        for link in vacancy:
            yield response.follow( link, self.vacancy_parse )

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath( '//div[contains(@class, "_3zucV")]//h1[contains(@class, "_3mfro")]/text()').get()
        salary = response.xpath( '//span[contains(@class, "_3mfro") and contains(@class,"_2Wp8I") and contains(@class,"ZON4b")]/*').getall()
        description = response.xpath( '//span[contains(@class, "_3mfro") and contains(@class,"_2LeqZ") and contains(@class,"_1hP6a")]/span/text()').getall()
        yield JobparserItem( name=name, salary=salary, description=description )