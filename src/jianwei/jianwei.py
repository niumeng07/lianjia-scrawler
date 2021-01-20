# -*- coding=utf-8 -*-
from __future__ import print_function
import requests
from bs4 import BeautifulSoup
import peewee

BASE_URL = 'http://210.75.213.188/shh/portal/bjjs2016/'
PAGE = 2940

username = 'root'
password = ''
dbname = 'ershoufang'
host = '127.0.0.1'

database = peewee.MySQLDatabase(
    dbname,
    host=host,
    port=3306,
    user=username,
    passwd=password,
    charset='utf8',
    use_unicode=True,
)


class BaseModel(peewee.Model):
    def __init__(self):
        pass

    class Meta:
        def __init__(self):
            super().__init__()
            pass
        database = database


class HouseJianwei(BaseModel):
    def __init__(self):
        super().__init__()
    id = peewee.PrimaryKeyField()
    district = peewee.CharField()
    name = peewee.CharField()
    type = peewee.CharField()
    square = peewee.FloatField()
    price = peewee.FloatField()
    agency = peewee.CharField()
    time = peewee.DateField()
    url = peewee.CharField()
    direction = peewee.CharField()
    floor = peewee.CharField()
    total_floor = peewee.CharField()
    year = peewee.IntegerField()
    decoration = peewee.CharField()


def database_init():
    database.connect()
    database.create_tables([HouseJianwei], safe=True)
    database.close()


def get_source_code(url):
    try:
        result = requests.get(url)
        source_code = result.content
    except Exception as e:
        print(e)
        return None

    return source_code


def parse_house(url, info_dict):
    source_code = get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    divtag = soup.find_all('div', class_="infolist_box")
    tds = []
    for dttag in divtag:
        bodytag = dttag.find_all("tbody")
        for body in bodytag:
            trtag = body.find_all("tr")
            for tr in trtag:
                tds.append(tr.findAll('td'))
    try:
        info_dict.update({'direction': tds[1][1].get_text().strip()})
        info_dict.update({'floor': tds[3][0].get_text().strip()})
        info_dict.update({'total_floor': tds[3][1].get_text().strip()})
        info_dict.update({'year': tds[4][0].get_text().strip()})
        info_dict.update({'decoration': tds[5][0].get_text().strip()})
    except:
        pass
    HouseJianwei.insert(**info_dict).upsert().execute()


database_init()
for i in range(0, PAGE + 1):
    tds = []
    source_code = get_source_code(BASE_URL + 'list.aspx?pagenumber=' + str(i))
    if source_code is None:
        continue
    soup = BeautifulSoup(source_code, 'lxml')
    divtag = soup.find_all('div', class_="infolist_box")
    for dttag in divtag:
        bodytag = dttag.find_all("tbody")
        for body in bodytag:
            trtag = body.find_all("tr")
            for tr in trtag:
                tds.append(tr.findAll('td'))
    for td in tds:
        info_dict = {}
        info_dict.update({'id': td[0].get_text().strip()})
        info_dict.update({'district': td[1].get_text().strip()})
        info_dict.update({'name': td[2].get_text().strip()})
        info_dict.update({'type': td[3].get_text().strip()})
        info_dict.update({'square': td[4].get_text().strip()})
        info_dict.update({'price': td[5].get_text().strip()[:-2]})
        info_dict.update({'agency': td[6].get_text().strip()})
        info_dict.update({'time': td[7].get_text().strip()})
        info_dict.update({'url': BASE_URL + td[8].a.get('href')})
        parse_house(BASE_URL + td[8].a.get('href'), info_dict)
    print('Page%d Finish' % i)
