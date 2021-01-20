# -*- coding: UTF-8 -*-
from __future__ import print_function
import argparse
import logging
import multiprocessing
import os
import sys

import core
import model
import settings

parser = argparse.ArgumentParser()
parser.add_argument('--updateSellCommunity', action='store_true', default=False)
parser.add_argument('--updateRent', action='store_true', default=False)
parser.add_argument('--updateCommunity', action='store_true', default=False)
parser.add_argument('--initDatabase', action='store_true', default=False)
parser.add_argument('--updateHouseAll', action='store_true', default=False)
parser.add_argument('--updateHouseCommunity', action='store_true', default=False)
parser.add_argument('--updateNeeds', action='store_true', default=False)
parser.add_argument('--isDebug', action='store_true', default=False)

args = parser.parse_args()

def get_communitylist(city):
    houses = model.Community.select().where(model.Community.city == city).order_by(model.Community.id)
    return [house.title for house in houses]


def dump_db(name):
    os.system("/usr/local/bin/mysqldump --databases {} > data/{}.sql".format(name, name))
    os.system("/bin/rm -rf data/{}.sql.tar.gz".format(name))
    os.system("tar -czvf data/{}.sql.tar.gz data/{}.sql".format(name, name))
    os.system("git add data/{}.sql.tar.gz".format(name))
    os.system("git commit -m 'update {}.'".format(name))
    os.system("git push origin -f")


def mysql_status():
    ret = os.system("/usr/local/bin/mysql.server status")
    if ret == 0:
        return ret
    os.system("/usr/local/bin/mysql.server start")
    ret = os.system("/usr/local/bin/mysql.server status")
    if ret == 0:
        return ret
    return 1


if __name__ == "__main__":
    ret = mysql_status()
    if ret != 0:
        print('mysql start failed.')
        sys.exit()

    regionlist = settings.REGIONLIST  # only pinyin support
    city = settings.CITY
    if args.initDatabase:
        model.database_init()  # create_tables: 执行一次即可

    # Init,scrapy celllist and insert database; could run only 1st time

    if args.updateCommunity:
        core.GetCommunityByRegionlist(city, regionlist)      # 获取小区列表写入表community

    communitylist = get_communitylist(city)              # Read celllist from database

    # for community in communitylist:
    #     logging.info("%s", community)

    if args.isDebug:
        # dump_db('ershoufang')
        # core.get_sell_percommunity(city, communitylist[0])
        # core.get_house_percommunity(city, communitylist[0])
        # core.get_community_perregion(city, 'chaoyang')
        # core.get_house_perregion(city, 'chaoyang')
        # core.get_rent_percommunity(city, 'chaoyang')
        sys.exit()

    pool = multiprocessing.Pool(processes=settings.CoreNums)

    if args.updateHouseCommunity:
        pool.apply_async(core.GetHouseByCommunitylist, args=(city, communitylist))

    if args.updateHouseAll or args.updateNeeds:
        pool.apply_async(core.GetHouseByRegionlist, args=(city, regionlist))

    if args.updateSellCommunity or args.updateNeeds:
        pool.apply_async(core.GetSellByCommunitylist, args=(city, communitylist))

    if args.updateRent:
        pool.apply_async(core.GetRentByCommunitylist, args=(city, communitylist))

    pool.close()
    pool.join()
    logging.info("All children process success.")

    if args.updateNeeds:
        dump_db('ershoufang')
        logging.info("dump ershoufang succcess.")
