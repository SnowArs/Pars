import requests
from lxml import html
from pprint import pprint
from datetime import datetime, date, time
from pymongo import MongoClient

client = MongoClient( 'localhost', 27017 )
client.drop_database( 'news' )
db = client['news']
base_lenta = db.lenta
base_mail = db.mail

class Site():
    def __init__(self, link, headers={'User-agent': 'Chrome/76.0.3809.132'}):
        self.link = link
        self.headers = headers
    def __str__(self):
        return f'{self.link}, {self.headers}'
    def getItem(self, path):
        req = requests.get(self.link).text
        root = html.fromstring(req)
        return root.xpath(path)

def fill_base(site_name, base, main_link, news, link, date):
    if site_name == 'Лента':
        for i in range(0, len(news)):
            base.insert_one( {f'Новость на сайте {site_name} ': news[i].replace('\xa0', ' '),
                                'Ссылка на новость ': main_link+link[i],
                                'Дата': date[i]} )
    else:
        for i in range( 0, len( news ) ):
            base.insert_one( {f'Новость на сайте {site_name} ': news[i].replace( '\xa0', ' ' ),
                              'Ссылка на новость ': main_link + link[i],
                              'Дата': date} )

mail = Site('https://mail.ru/')
lenta = Site('https://lenta.ru/')

mail_news = mail.getItem('//div[@class="news__list__item__wrap"]//span[@class="news__list__item__link__text"][1]/text()')
mail_links = mail.getItem('//a[@class="news__list__item__link news__list__item__link_simple"]/@href')
mail_date = datetime.now().strftime('%Y-%m-%d %H:%M')

lenta_news = lenta.getItem('//section[@class="row b-top7-for-main js-top-seven"]//div[@class="item"]/a[last()]/text()|\
                    //div[@class="first-item"]//h2//a[last()]/text()')
lenta_links = lenta.getItem('//section[@class="row b-top7-for-main js-top-seven"]//div[@class="item"]/a/@href |\
                    //div[@class="first-item"]//h2//a/@href')
lenta_date = lenta.getItem('//div[@class="first-item"]//time/@datetime | //time/@datetime')
mail_news1 = mail.getItem('//a[@class="news__list__item__link news__list__item__link_simple"]/span/text()')



fill_base('Лента', base_lenta, lenta.link, lenta_news, lenta_links, lenta_date  )
fill_base('MAIL', base_mail, mail.link, mail_news, mail_links, mail_date  )

collections = db.list_collection_names()
for col in collections:
    col_str = str( col )
    for item in db[col_str].find():
        print( item )