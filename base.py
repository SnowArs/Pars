import time
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient

client = MongoClient( 'localhost', 27017 )
client.drop_database( 'vacancy_base' )
db = client['vacancy_base']
baseHH = db.HH
baseSJ = db.SJ


class Site_prep:
    def __init__(self, link, vacancy='логист', headers={'User-agent': 'Chrome/76.0.3809.132'}):
        self.link = link
        self.vacancy = vacancy
        self.headers = headers

    def requestedHH(self):
        return requests.get( self.link + '/search/vacancy?area=1&st=searchVacancy&text=' \
                             + self.vacancy, headers=self.headers ).text

    def requestedSJ(self):
        return requests.get( self.link + '/vacancy/search/?keywords=' \
                             + self.vacancy, headers=self.headers ).text

    def __str__(self):
        return f'{self.link}, {self.vacancy}'


def parsed(x):
    return bs( x, 'html.parser' )


class Retriver():
    def __init__(self, html):
        self.html = html

    def dataHH(self):
        return self.html.findAll( 'div', {'class': ['vacancy-serp-item', \
                                                    'vacancy-serp-item_premium']} )

    def dataSJ(self):
        return self.html.select( 'div._3syPg._1_bQo._2FJA4' )


def collect_infoHH(row_vacancy, sec, vac_df):
    for vac in row_vacancy:
        sec += 1
        salary = vac.find( 'div', {'class': 'vacancy-serp-item__compensation'} )
        vacancy_info = vac.find( 'span', {'class': 'g-user-content'} ).findChild()
        vacancy_name = vacancy_info.getText()
        link = vacancy_info['href']
        vac_df.loc[sec, 'вакансия'] = vacancy_name
        vac_df.loc[sec, 'ссылка на вакансию'] = link
        vac_df.loc[sec, 'сайт'] = 'HH'
        if not salary:
            vac_df.loc[sec, 'ЗП мин'] = 'нет информации'
            vac_df.loc[sec, 'ЗП макс'] = 'нет информации'
        else:
            salary = salary.getText().replace( '\xa0', '' )
            if '-' in salary:
                vac_df.loc[sec, 'ЗП мин'] = int( salary[:salary.find( '-' )] )
                vac_df.loc[sec, 'ЗП макс'] = int( salary[salary.find( '-' ) + 1:-5] )
            else:
                ZP = int(
                    vac.find( 'div', {'class': 'vacancy-serp-item__compensation'} ).getText().replace( '\xa0', '' )[
                    3:-5] )
                vac_df.loc[sec, 'ЗП мин'] = ZP
                vac_df.loc[sec, 'ЗП макс'] = 'нет информации'
        baseHH.insert_one( {'вакансия': vacancy_name,
                            'ссылка на вакансию': link,
                            'ЗП мин': vac_df.loc[sec, 'ЗП мин'],
                            'ЗП макс': vac_df.loc[sec, 'ЗП макс']} )
    return vac_df, baseHH, sec


def next_pageHH(parsed_html):
    page_next = parsed_html.find( 'span', {'class': 'bloko-button-group'} ).findChildren()
    next_page = page_next[3].find( 'a' )['href']
    if next_page:
        html = requests.get( 'https://hh.ru' + next_page, headers=headers ).text
        parsed_html = bs( html, 'html.parser' )
        row_vacancy = parsed_html.findAll( 'div', {'class': ['vacancy-serp-item', 'vacancy-serp-item_premium']} )
        return row_vacancy, parsed_html
    else:
        return error


def collect_infoSJ(row_vacancy, sec, vac_df):
    for row in range( 0, len( row_vacancy ) - 1 ):
        sec += 1
        vacancy_name = row_vacancy[row].select( 'a.icMQ_._1QIBo' )[0].getText()
        link = 'https://www.superjob.ru' + row_vacancy[row].find( 'a', {'class': ['icMQ_', '_1QIBo']} )['href']
        vac_df.loc[sec, 'вакансия'] = vacancy_name
        vac_df.loc[sec, 'ссылка на вакансию'] = link
        vac_df.loc[sec, 'сайт'] = 'SJ'
        try:
            ZP_children = row_vacancy[row].find( 'span', {'class': ['3mfro', '_2Wp8I']} ).findChildren()
            if len( ZP_children ) > 2:
                vac_df.loc[sec, 'ЗП мин'] = int( ZP_children[0].getText().replace( '\xa0', '' ) )
                vac_df.loc[sec, 'ЗП макс'] = int( ZP_children[2].getText().replace( '\xa0', '' ) )
            else:
                vac_df.loc[sec, 'ЗП мин'] = int( ZP_children[0].getText().replace( '\xa0', '' ) )
                vac_df.loc[sec, 'ЗП макс'] = "нет информации"
        except:
            vac_df.loc[sec, 'ЗП мин'] = "нет информации"

        baseSJ.insert_one( {'вакансия': vacancy_name,
                            'ссылка на вакансию': link,
                            'ЗП мин': vac_df.loc[sec, 'ЗП мин'],
                            'ЗП макс': vac_df.loc[sec, 'ЗП макс']} )
    return vac_df, baseSJ, sec


def next_pageSJ(parsed_html):
    page_next = parsed_html.find( 'span', {'class': 'bloko-button-group'} ).findChildren()
    next_page = page_next[3].find( 'a' )['href']
    if next_page:
        html = requests.get( 'https://hh.ru' + next_page, headers=headers ).text
        parsed_html = bs( html, 'html.parser' )
        row_vacancy = parsed_html.findAll( 'div', {'class': ['vacancy-serp-item', 'vacancy-serp-item_premium']} )
        return row_vacancy, parsed_html
    else:
        return error


vacancy = str( input( 'введите должность :' ) )
link_HH = Site_prep( 'https://www.hh.ru', vacancy )
link_SJ = Site_prep( 'https://www.superjob.ru', vacancy )
sec = 0
html_HH = parsed( link_HH.requestedHH() )
html_SJ = parsed( link_SJ.requestedSJ() )
vac_df = pd.DataFrame( columns=['вакансия', 'ЗП мин', 'ЗП макс', 'сайт', 'ссылка на вакансию'] )
pd.set_option( 'display.max_colwidth', 15 )

row_vacancy_HH = Retriver( html_HH )
row_vacancy_SJ = Retriver( html_SJ )

for pages in range( 1, 3 ):  # page_numbers

    try:
        vac_df, baseSJ, sec = collect_infoSJ( row_vacancy_SJ.dataSJ(), sec, vac_df )
        collect_infoSJ, html_SJ, = next_pageSJ( html_SJ )
    except:
        time.sleep( 2 )

for pages in range( 1, 3 ):  # page_numbers

    try:
        vac_df, baseHH, sec = collect_infoHH( row_vacancy_HH.dataHH(), sec, vac_df )
        collect_infoHH, html_HH, = next_pageHH( html_HH )


    except:
        time.sleep( 2 )

while True:
    to_print = str( input( 'вы хотите вывести список вакансий да/нет ' ) )
    if to_print == 'да':
        collections = db.list_collection_names()
        for col in collections:
            col_str = str( col )
            print(f'Вакансии с сайта {col}')
            for item in db[col_str].find():
                print( item )
        else:
            to_print_whish = str( input( 'вы хотите вывести список вакансий удовлетворяющих желаемой ЗП, да/нет ' ) )
            wish_zp = int( input( 'введите  ЗП от :' ) )
            if to_print == 'да':
                collections = db.list_collection_names()
                for col in collections:
                    col_str = str( col )
                    print( f'Вакансии с сайта {col}' )
                    for item in db[col_str].find( {'ЗП мин': {'$gte': wish_zp}},
                                                  {'вакансия', 'ссылка на вакансию'} ):
                        print( item )
    else:
        break
