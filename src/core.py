# -*- coding: utf-8 -*-
from __future__ import print_function

import concurrent
import datetime
import logging
import traceback
import urllib2
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import settings
import misc
import model

exector = concurrent.futures.ThreadPoolExecutor(settings.ThreadNums)


def GetHouseByCommunitylist(city, communitylist):
    logging.info("Get House Infomation")
    starttime = datetime.datetime.now()
    futures = []
    for community in communitylist:
        futures.append(exector.submit(get_house_percommunity, city, community))
    concurrent.futures.wait(futures)
    endtime = datetime.datetime.now()
    logging.info("Get House Infomation success. Run time: %s", str(endtime - starttime))


def GetSellByCommunitylist(city, communitylist):
    logging.info("Get Sell Infomation")
    starttime = datetime.datetime.now()
    futures = []
    for community in communitylist:
        futures.append(exector.submit(get_sell_percommunity, city, community))
    concurrent.futures.wait(futures)
    endtime = datetime.datetime.now()
    logging.info("Get Sell Infomation success, Run time: %s", str(endtime - starttime))


def GetRentByCommunitylist(city, communitylist):
    logging.info("Get Rent Infomation")
    starttime = datetime.datetime.now()
    futures = []
    for community in communitylist:
        futures.append(exector.submit(get_rent_percommunity, city, community))
    concurrent.futures.wait(futures)
    endtime = datetime.datetime.now()
    logging.info("Get Rent Infomation success, Run time: %s", str(endtime - starttime))


def GetCommunityByRegionlist(city, regionlist=[u'xicheng']):
    logging.info("Get Community Infomation")
    starttime = datetime.datetime.now()
    futures = []
    for regionname in regionlist:
        futures.append(exector.submit(get_community_perregion, city, regionname))
    concurrent.futures.wait(futures)
    endtime = datetime.datetime.now()
    logging.info("Get Community Infomation success, Run time: %s", str(endtime - starttime))


def GetHouseByRegionlist(city, regionlist=[u'xicheng']):
    logging.info("Get Onsale House Infomation")
    starttime = datetime.datetime.now()
    futures = []
    for regionname in regionlist:
        futures.append(exector.submit(get_house_perregion, city, regionname))
    concurrent.futures.wait(futures)
    endtime = datetime.datetime.now()
    logging.info("Get Onsale House Infomation success, Run time: %s", str(endtime - starttime))


def GetRentByRegionlist(city, regionlist=[u'xicheng']):
    logging.info("Get Rent House Infomation")
    starttime = datetime.datetime.now()
    futures = []
    for regionname in regionlist:
        futures.append(exector.submit(get_rent_perregion, city, regionname))
    concurrent.futures.wait(futures)
    endtime = datetime.datetime.now()
    logging.info("Get Rent House Infomation success, Run time: %s", str(endtime - starttime))


def get_house_percommunity(city, communityname):
    try:
        baseUrl = u"http://%s.lianjia.com/" % (city)
        url = baseUrl + u"ershoufang/rs" + urllib2.quote(communityname.encode('utf8')) + "/"
        source_code = misc.get_source_code(url)
        soup = BeautifulSoup(source_code, 'lxml')

        if check_block(soup):
            return
        total_pages = misc.get_total_pages(url)

        if total_pages is None:
            row = model.Houseinfo.select().count()
            raise RuntimeError("Finish at %s because total_pages is None" % row)

        for page in range(total_pages):
            if page > 0:
                url_page = baseUrl + \
                    u"ershoufang/pg%drs%s/" % (page,
                                               urllib2.quote(communityname.encode('utf8')))
                source_code = misc.get_source_code(url_page)
                soup = BeautifulSoup(source_code, 'lxml')

            nameList = soup.findAll("li", {"class": "clear"})
            i = 0
            logging.info("Progress: %s %s: current page %s total pages %s", "GetHouseByCommunitylist", communityname, page + 1, total_pages)
            data_source = []
            hisprice_data_source = []
            for name in nameList:  # per house loop
                i = i + 1
                info_dict = {}
                try:
                    housetitle = name.find("div", {"class": "title"})
                    info_dict.update({u'title': housetitle.a.get_text().strip()})
                    info_dict.update({u'link': housetitle.a.get('href')})

                    houseaddr = name.find("div", {"class": "address"})
                    info = houseaddr.div.get_text().split('|')
                    info_dict.update({u'community': communityname})
                    info_dict.update({u'housetype': info[0].strip()})
                    info_dict.update({u'square': info[1].strip()})
                    if len(info) > 6:
                        info_dict.update({u'direction': info[2].strip() + "-" + info[6].strip()})
                    else:
                        info_dict.update({u'direction': info[2].strip()})

                    info_dict.update({u'decoration': info[3].strip()})
                    if len(info) > 5:
                        info_dict.update({u'years': info[5].strip()})
                    else:
                        info_dict.update({u'years': ''})
                    if len(info) > 6:
                        info_dict.update({u'towertype': info[6]})
                    else:
                        info_dict.update({u'towertype': None})

                    housefloor = name.find("div", {"class": "positionInfo"})
                    communityInfo = housefloor.get_text().split('-')
                    if len(communityInfo) > 1:
                        info_dict.update({u'business': communityInfo[1]})
                    else:
                        info_dict.update({u'business': None})

                    housefloor = name.find("div", {"class": "flood"})
                    floor_all = housefloor.div.get_text().split(
                        '-')[0].strip().split(' ')
                    if len(info) > 5:
                        info_dict.update({u'floor': floor_all[0].strip() + '-' + info[4].strip()})
                    else:
                        info_dict.update({u'floor': floor_all[0].strip() + '-'})

                    followInfo = name.find("div", {"class": "followInfo"})
                    info_dict.update({u'followInfo': followInfo.get_text()})

                    tax = name.find("div", {"class": "tag"})
                    info_dict.update({u'taxtype': tax.get_text().strip()})

                    totalPrice = name.find("div", {"class": "totalPrice"})
                    info_dict.update({u'totalPrice': totalPrice.span.get_text()})

                    unitPrice = name.find("div", {"class": "unitPrice"})
                    info_dict.update({u'unitPrice': unitPrice.get('data-price')})
                    info_dict.update({u'houseID': unitPrice.get('data-hid')})
                except Exception as e:
                    print(e, traceback.print_exc())
                    logging.info('parse error: %s', name)
                    continue
                data_source.append(info_dict)
                hisprice_data_source.append(
                    {"houseID": info_dict["houseID"], "totalPrice": info_dict["totalPrice"]})

            with model.database.atomic():
                if data_source:
                    logging.info("get_house_percommunity: insert %d house info to database", len(data_source))
                    model.Houseinfo.insert_many(data_source).upsert().execute()
                if hisprice_data_source:
                    logging.info("get_house_percommunity: insert %d hisprice data source info to database", len(hisprice_data_source))
                    model.Hisprice.insert_many(
                        hisprice_data_source).upsert().execute()
    except Exception as e:
        print(e, traceback.print_exc())


def get_sell_percommunity(city, communityname):
    try:
        baseUrl = u"http://%s.lianjia.com/" % (city)
        url = baseUrl + u"chengjiao/rs" + \
            urllib2.quote(communityname.encode('utf8')) + "/"
        source_code = misc.get_source_code(url)
        soup = BeautifulSoup(source_code, 'lxml')

        if check_block(soup):
            return
        total_pages = misc.get_total_pages(url)

        if total_pages is None:
            row = model.Sellinfo.select().count()
            raise RuntimeError("Finish at %s because total_pages is None" % row)

        for page in range(total_pages):
            if page > 0:
                url_page = baseUrl + \
                    u"chengjiao/pg%drs%s/" % (page,
                                              urllib2.quote(communityname.encode('utf8')))
                source_code = misc.get_source_code(url_page)
                soup = BeautifulSoup(source_code, 'lxml')

            logging.info("Progress: %s %s: current page %s total pages %s", "GetSellByCommunitylist", communityname, page + 1, total_pages)
            data_source = []
            for ultag in soup.findAll("ul", {"class": "listContent"}):
                for name in ultag.find_all('li'):
                    info_dict = {}
                    try:
                        try:
                            dealinfo = name.find('div', {'class': 'dealCycleeInfo'}).find('span', {'class': 'dealCycleTxt'})
                            info_dict.update({u'dealinfo': dealinfo.get_text().strip()})  # 挂牌价和交易周期
                        except Exception as e:
                            info_dict.update({u'dealinfo': ''})
                        housetitle = name.find("div", {"class": "title"})
                        info_dict.update({u'title': housetitle.get_text().strip()})
                        info_dict.update({u'link': housetitle.a.get('href')})
                        houseID = housetitle.a.get(
                            'href').split("/")[-1].split(".")[0]
                        info_dict.update({u'houseID': houseID.strip()})

                        house = housetitle.get_text().strip().split(' ')
                        info_dict.update({u'community': communityname})
                        info_dict.update(
                            {u'housetype': house[1].strip() if len(house) > 1 else ''})
                        info_dict.update(
                            {u'square': house[2].strip() if len(house) > 2 else ''})

                        houseinfo = name.find("div", {"class": "houseInfo"})
                        info = houseinfo.get_text().split('|')
                        info_dict.update({u'direction': info[0].strip()})
                        info_dict.update(
                            {u'status': info[1].strip() if len(info) > 1 else ''})

                        housefloor = name.find("div", {"class": "positionInfo"})
                        floor_all = housefloor.get_text().strip().split(' ')
                        info_dict.update({u'floor': floor_all[0].strip()})
                        info_dict.update({u'years': floor_all[-1].strip()})

                        followInfo = name.find("div", {"class": "source"})
                        info_dict.update(
                            {u'source': followInfo.get_text().strip()})

                        totalPrice = name.find("div", {"class": "totalPrice"})
                        if totalPrice.span is None:
                            info_dict.update(
                                {u'totalPrice': totalPrice.get_text().strip()})
                        else:
                            info_dict.update(
                                {u'totalPrice': totalPrice.span.get_text().strip()})

                        unitPrice = name.find("div", {"class": "unitPrice"})
                        if unitPrice.span is None:
                            info_dict.update(
                                {u'unitPrice': unitPrice.get_text().strip()})
                        else:
                            info_dict.update(
                                {u'unitPrice': unitPrice.span.get_text().strip()})

                        dealDate = name.find("div", {"class": "dealDate"})
                        info_dict.update(
                            {u'dealdate': dealDate.get_text().strip().replace('.', '-')})

                    except Exception as e:
                        print(e, traceback.print_exc())
                    data_source.append(info_dict)
                    # model.Sellinfo.insert(**info_dict).upsert().execute()

            with model.database.atomic():
                if data_source:
                    logging.info("get_sell_percommunity: insert %d sell info data source info to database", len(data_source))
                    model.Sellinfo.insert_many(data_source).upsert().execute()
    except Exception as e:
        print(e, traceback.print_exc())


def get_community_perregion(city, regionname=u'xicheng'):
    try:
        baseUrl = u"http://%s.lianjia.com/" % (city)
        url = baseUrl + u"xiaoqu/" + regionname + "/"
        source_code = misc.get_source_code(url)
        soup = BeautifulSoup(source_code, 'lxml')

        if check_block(soup):
            return
        total_pages = misc.get_total_pages(url)

        if total_pages is None:
            row = model.Community.select().count()
            raise RuntimeError("Finish at %s because total_pages is None" % row)

        for page in range(total_pages):
            if page > 0:
                url_page = baseUrl + u"xiaoqu/" + regionname + "/pg%d/" % page
                source_code = misc.get_source_code(url_page)
                soup = BeautifulSoup(source_code, 'lxml')

            nameList = soup.findAll("li", {"class": "clear"})
            i = 0
            logging.info("Progress: %s %s: current page %s total pages %s", "GetCommunityByRegionlist", regionname, page + 1, total_pages)
            data_source = []
            for name in nameList:  # Per house loop
                i = i + 1
                info_dict = {}
                try:
                    communitytitle = name.find("div", {"class": "title"})
                    title = communitytitle.get_text().strip('\n')
                    link = communitytitle.a.get('href')
                    info_dict.update({u'title': title})
                    info_dict.update({u'link': link})

                    district = name.find("a", {"class": "district"})
                    info_dict.update({u'district': district.get_text()})

                    bizcircle = name.find("a", {"class": "bizcircle"})
                    info_dict.update({u'bizcircle': bizcircle.get_text()})

                    tagList = name.find("div", {"class": "tagList"})
                    info_dict.update({u'tagList': tagList.get_text().strip('\n')})

                    onsale = name.find("a", {"class": "totalSellCount"})
                    info_dict.update(
                        {u'onsale': onsale.span.get_text().strip('\n')})

                    onrent = name.find("a", {"title": title + u"租房"})
                    info_dict.update(
                        {u'onrent': onrent.get_text().strip('\n').split(u'套')[0]})

                    info_dict.update({u'id': name.get('data-housecode')})

                    price = name.find("div", {"class": "totalPrice"})
                    info_dict.update({u'price': price.span.get_text().strip('\n')})

                    communityinfo = get_communityinfo_by_url(link)
                    for key, value in communityinfo.iteritems():
                        info_dict.update({key: value})

                    info_dict.update({u'city': city})
                except Exception as e:
                    print(e, traceback.print_exc())
                    continue
                # communityinfo insert into mysql
                data_source.append(info_dict)
            with model.database.atomic():
                if data_source:
                    logging.info("get_community_perregion: insert %d community info to database", len(data_source))
                    model.Community.insert_many(data_source).upsert().execute()
            # time.sleep(1)
    except Exception as e:
        print(e, traceback.print_exc())

def get_rent_percommunity(city, communityname):
    try:
        baseUrl = u"http://%s.lianjia.com/" % (city)
        url = baseUrl + u"zufang/rs" + \
            urllib2.quote(communityname.encode('utf8')) + "/"
        source_code = misc.get_source_code(url)
        soup = BeautifulSoup(source_code, 'lxml')

        if check_block(soup):
            logging.info('soup error')
            return
        total_pages = misc.get_total_pages(url)

        if total_pages is None:
            row = model.Rentinfo.select().count()
            raise RuntimeError("Finish at %s because total_pages is None" % row)

        for page in range(total_pages):
            if page > 0:
                url_page = baseUrl + u"rent/pg%drs%s/" % (page, urllib2.quote(communityname.encode('utf8')))
                source_code = misc.get_source_code(url_page)
                soup = BeautifulSoup(source_code, 'lxml')
            i = 0
            data_source = []
            for ultag in soup.findAll("div", {"class": "content__list"}):
                for name in ultag.find_all("div", {"class": "content__list--item"}):
                    i = i + 1
                    info_dict = {}
                    try:
                        housetitle = name.find("div", {"class": "content__list--item--main"})
                        info_dict.update({u'title': housetitle.find('p', {"class": "content__list--item--title"}).find('a', {'class': "twoline"}).get_text().strip()})
                        subway = name.find('i', {"class": "content__item__tag--is_subway_house"})
                        if subway is None:
                            info_dict.update({u'subway': ""})
                        else:
                            info_dict.update({u'subway': subway.get_text().strip()})

                        decoration = name.find('i', {"class": 'content__item__tag--decoration'})
                        if decoration is None:
                            info_dict.update({u'decoration': ""})
                        else:
                            info_dict.update(
                                {u'decoration': decoration.get_text().strip()})

                        houseID = housetitle.a.get(
                            'href').split("/")[-1].split(".")[0]
                        info_dict.update({u'houseID': houseID})
                        region = name.find('p', {"class": "content__list--item--des"}).find('a')
                        if region is None:
                            region = ""
                        else:
                            region = region.get_text().strip()
                        info_dict.update({u'region': region})

                        zone = name.find('p', {"class": "content__list--item--des"}).find_all('a')[1]
                        if zone is None:
                            zone = ""
                        else:
                            zone = zone.get_text().strip()
                        info_dict.update({u'zone': zone})

                        price = name.find("span", {"class": "content__list--item-price"})
                        if price is None:
                            price = ""
                        else:
                            price = price.get_text().strip()
                        info_dict.update({u'price': price})

                        heating = name.find("i", {"class": "content__item__tag--central_heating"})
                        if heating is None:
                            heating = ""
                        else:
                            heating = heating.get_text().strip()
                        info_dict.update({u'heating': heating})

                        other = name.find('p', {"class": "content__list--item--des"})
                        if other is not None:
                            other = other.get_text().replace('\n', '').replace(' ', '').strip()
                        else:
                            other = "-/-/-/-/-"
                        info_dict.update({u'other': other})

                        # position, meters, direction, rooms, desc = other.split('/')
                        # info_dict.update({u'meters': meters})
                        info_dict.update({u'meters': ""})

                        pricepre = ''
                        info_dict.update({u'pricepre': pricepre})

                        info_dict.update({u'link': 'https://bj.lianjia.com/zufang' + housetitle.a.get('href')})

                    except Exception as e:
                        print(e, traceback.print_exc())
                    data_source.append(info_dict)

            with model.database.atomic():
                if data_source:
                    logging.info("get_rent_percommunity: insert %d rent info to database", len(data_source))
                    model.Rentinfo.insert_many(data_source).upsert().execute()
            # time.sleep(1)
    except Exception as e:
        print(e, traceback.print_exc())


def get_house_perregion(city, district):
    try:
        baseUrl = u"http://%s.lianjia.com/" % (city)
        url = baseUrl + u"ershoufang/%s/" % district
        source_code = misc.get_source_code(url)
        soup = BeautifulSoup(source_code, 'lxml')
        if check_block(soup):
            return
        total_pages = misc.get_total_pages(url)
        if total_pages is None:
            row = model.Houseinfo.select().count()
            raise RuntimeError("Finish at %s because total_pages is None" % row)

        for page in range(total_pages):
            if page > 0:
                url_page = baseUrl + u"ershoufang/%s/pg%d/" % (district, page)
                source_code = misc.get_source_code(url_page)
                soup = BeautifulSoup(source_code, 'lxml')
            i = 0
            logging.info("Progress: %s %s: current page %s total pages %s", "GetHouseByRegionlist", district, page + 1, total_pages)
            data_source = []
            hisprice_data_source = []
            for ultag in soup.findAll("ul", {"class": "sellListContent"}):
                for name in ultag.find_all('li'):
                    i = i + 1
                    info_dict = {}
                    try:
                        housetitle = name.find("div", {"class": "title"})
                        info_dict.update({u'title': housetitle.a.get_text().strip()})
                        info_dict.update({u'link': housetitle.a.get('href')})

                        houseID = housetitle.a.get('data-housecode')
                        info_dict.update({u'houseID': houseID})

                        houseinfo = name.find("div", {"class": "houseInfo"})
                        info = houseinfo.get_text().split('|')
                        if len(info) > 0:
                            info_dict.update({u'housetype': info[0]})
                        else:
                            info_dict.update({u'housetype': ""})
                        if len(info) > 1:
                            info_dict.update({u'square': info[1]})
                        else:
                            info_dict.update({u'square': ""})
                        if len(info) > 2:
                            info_dict.update({u'direction': info[2]})
                        else:
                            info_dict.update({u'direction': ""})
                        if len(info) > 3:
                            info_dict.update({u'decoration': info[3]})
                        else:
                            info_dict.update({u'decoration': ""})
                        if len(info) > 4:
                            info_dict.update({u'floor': info[4]})
                        else:
                            info_dict.update({u'floor': ""})
                        if len(info) > 5:
                            info_dict.update({u'years': info[5]})
                        else:
                            info_dict.update({u'years': ""})
                        if len(info) > 6:
                            info_dict.update({u'towertype': info[6]})
                        else:
                            info_dict.update({u'towertype': ""})

                        housefloor = name.find("div", {"class": "positionInfo"})
                        communityInfo = housefloor.get_text().split('-')
                        info_dict.update({u'community': communityInfo[0]})
                        if len(communityInfo) > 1:
                            info_dict.update({u'business': communityInfo[1]})
                        else:
                            info_dict.update({u'business': ""})

                        followInfo = name.find("div", {"class": "followInfo"})
                        info_dict.update(
                            {u'followInfo': followInfo.get_text().strip()})

                        taxfree = name.find("span", {"class": "taxfree"})
                        if taxfree is None:
                            info_dict.update({u"taxtype": ""})
                        else:
                            info_dict.update(
                                {u"taxtype": taxfree.get_text().strip()})

                        totalPrice = name.find("div", {"class": "totalPrice"})
                        info_dict.update(
                            {u'totalPrice': totalPrice.span.get_text()})

                        unitPrice = name.find("div", {"class": "unitPrice"})
                        info_dict.update(
                            {u'unitPrice': unitPrice.get("data-price")})
                    except Exception as e:
                        print(e, traceback.print_exc())
                        continue

                    # Houseinfo insert into mysql
                    data_source.append(info_dict)
                    hisprice_data_source.append(
                        {"houseID": info_dict["houseID"], "totalPrice": info_dict["totalPrice"]})
                    # model.Houseinfo.insert(**info_dict).upsert().execute()
                    # model.Hisprice.insert(houseID=info_dict['houseID'], totalPrice=info_dict['totalPrice']).upsert().execute()

            with model.database.atomic():
                if data_source:
                    logging.info("get_house_perregion: insert %d region info to database", len(data_source))
                    model.Houseinfo.insert_many(data_source).upsert().execute()
                if hisprice_data_source:
                    logging.info("get_house_perregion: insert %d region info to database", len(hisprice_data_source))
                    model.Hisprice.insert_many(
                        hisprice_data_source).upsert().execute()
            # time.sleep(1)
    except Exception as e:
        print(e, traceback.print_exc())


def get_rent_perregion(city, district):
    try:
        baseUrl = u"http://%s.lianjia.com/" % (city)
        url = baseUrl + u"zufang/%s/" % district
        source_code = misc.get_source_code(url)
        soup = BeautifulSoup(source_code, 'lxml')
        if check_block(soup):
            return
        total_pages = misc.get_total_pages(url)
        if total_pages is None:
            row = model.Rentinfo.select().count()
            raise RuntimeError("Finish at %s because total_pages is None" % row)

        for page in range(total_pages):
            if page > 0:
                url_page = baseUrl + u"zufang/%s/pg%d/" % (district, page)
                source_code = misc.get_source_code(url_page)
                soup = BeautifulSoup(source_code, 'lxml')
            i = 0
            logging.info("Progress: %s %s: current page %s total pages %s", "GetRentByRegionlist", district, page + 1, total_pages)
            data_source = []
            for ultag in soup.findAll("ul", {"class": "house-lst"}):
                for name in ultag.find_all('li'):
                    i = i + 1
                    info_dict = {}
                    try:
                        housetitle = name.find("div", {"class": "info-panel"})
                        info_dict.update(
                            {u'title': housetitle.h2.a.get_text().strip()})
                        info_dict.update({u'link': housetitle.a.get("href")})
                        houseID = name.get("data-housecode")
                        info_dict.update({u'houseID': houseID})

                        region = name.find("span", {"class": "region"})
                        info_dict.update({u'region': region.get_text().strip()})

                        zone = name.find("span", {"class": "zone"})
                        info_dict.update({u'zone': zone.get_text().strip()})

                        meters = name.find("span", {"class": "meters"})
                        info_dict.update({u'meters': meters.get_text().strip()})

                        other = name.find("div", {"class": "con"})
                        info_dict.update({u'other': other.get_text().strip()})

                        subway = name.find("span", {"class": "fang-subway-ex"})
                        if subway is None:
                            info_dict.update({u'subway': ""})
                        else:
                            info_dict.update(
                                {u'subway': subway.span.get_text().strip()})

                        decoration = name.find("span", {"class": "decoration-ex"})
                        if decoration is None:
                            info_dict.update({u'decoration': ""})
                        else:
                            info_dict.update(
                                {u'decoration': decoration.span.get_text().strip()})

                        heating = name.find("span", {"class": "heating-ex"})
                        if decoration is None:
                            info_dict.update({u'heating': ""})
                        else:
                            info_dict.update(
                                {u'heating': heating.span.get_text().strip()})

                        price = name.find("div", {"class": "price"})
                        info_dict.update(
                            {u'price': int(price.span.get_text().strip())})

                        pricepre = name.find("div", {"class": "price-pre"})
                        info_dict.update(
                            {u'pricepre': pricepre.get_text().strip()})

                    except Exception as e:
                        print(e, traceback.print_exc())
                        continue
                    # Rentinfo insert into mysql
                    data_source.append(info_dict)
                    # model.Rentinfo.insert(**info_dict).upsert().execute()

            with model.database.atomic():
                if data_source:
                    logging.info("get_rent_perregion: insert %d region info to database", len(data_source))
                    model.Rentinfo.insert_many(data_source).upsert().execute()
            # time.sleep(1)
    except Exception as e:
        print(e, traceback.print_exc())


def get_communityinfo_by_url(url):
    try:
        source_code = misc.get_source_code(url)
        soup = BeautifulSoup(source_code, 'lxml')

        res = {}
        if check_block(soup):
            return res

        communityinfos = soup.findAll("div", {"class": "xiaoquInfoItem"})
        for info in communityinfos:
            key_type = {
                u"建筑年代": u'year',
                u"建筑类型": u'housetype',
                u"物业费用": u'cost',
                u"物业公司": u'service',
                u"开发商": u'company',
                u"楼栋总数": u'building_num',
                u"房屋总数": u'house_num',
            }
            try:
                key = info.find("span", {"xiaoquInfoLabel"})
                value = info.find("span", {"xiaoquInfoContent"})
                key_info = key_type[key.get_text().strip()]
                value_info = value.get_text().strip()
                res.update({key_info: value_info})

            except Exception as e:
                # logging.error(e) # 这里不需要打印该log,多余的字段不需要解析
                # u"附近门店": u'store_near',
                continue
        return res
    except Exception as e:
        print(e, traceback.print_exc())


def check_block(soup):
    if soup.title.string == "414 Request-URI Too Large":
        logging.error(
            "Lianjia block your ip, please verify captcha manually at lianjia.com")
        return True
    return False
