# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient


class JobparserPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        client.drop_database( 'vacancy2' )
        self.mongo_base = client.vacancy2

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            description = ''.join( item['description'] )
            if any(map(str.isdigit, item['salary'])):
                salary_min = item['salary'].replace('\xa0','').split()[1]
                if any(map(str.isdigit, item['salary'].replace('\xa0' ,'').split()[3])):
                    salary_max = item['salary'].replace('\xa0' ,'').split()[3]
                else:
                    salary_max = ' з/п не указана'
            else:
                salary_min = item['salary']
                salary_max = item['salary']
        else:
            description = '.'.join( item['description'] )
            salary_min = item['salary'][0].replace('\xa0','')[6:-7]
            try:
                salary_max = item['salary'][2].replace( '\xa0', '' )[6:-7]
            except:
                salary_max = ' з/п не указана'

        collection = self.mongo_base[spider.name]
        collection.insert_one({f'вакансия сайта {spider.name}': item['name'],
                              'ЗП мин': salary_min,
                              'ЗП макс': salary_max,
                              'описание': description})

