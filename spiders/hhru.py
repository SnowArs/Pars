# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?area=113&st=searchVacancy&text=Логист']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').get()
        yield response.follow(next_page, callback=self.parse)
        vacancy = response.css(
            'div.vacancy-serp-item__row_header a.HH-LinkModifier::attr(href)').getall()
        for link in vacancy:
            yield response.follow(link, self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.css('div.vacancy-title h1.header span.highlighted::text').get()
        salary = response.css('div.vacancy-title p.vacancy-salary::text').get()
        description = response.css('div.g-user-content p *::text').getall()
        yield JobparserItem(name=name, salary=salary, description=description)
