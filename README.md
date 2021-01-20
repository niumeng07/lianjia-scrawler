# lianjia-scrawler
[![Licenses](https://img.shields.io/badge/license-bsd-orange.svg)](https://opensource.org/licenses/BSD-3-Clause)
添加了并行逻辑

## 使用说明
+ 下载源码并安装依赖包

+ 设置数据库信息以及爬取城市行政区信息（支持三种数据库格式）
```
DBENGINE = 'mysql' #ENGINE OPTIONS: mysql, sqlite3, postgresql
DBNAME = 'test'
DBUSER = 'root'
DBPASSWORD = ''
DBHOST = '127.0.0.1'
DBPORT = 3306
CITY = 'bj' # only one, shanghai=sh shenzhen=sh......
REGIONLIST = [u'chaoyang', u'xicheng'] # 只支持拼音
```

## 相关爬虫函数介绍
```
行政区列表：
regionlist = ['chaoyang', 'haidian'] 目前仅支持拼音
小区列表，可通过GetCommunityByRegionlist爬虫得到
communitylist = [u'万科星园', u'上地东里']

#table_name: community
根据行政区来爬虫小区信息, 返回regionlist里面所有小区信息。
core.GetCommunityByRegionlist(city, regionlist)

#table_name: houseinfo
根据行政区来爬虫在售房源信息， 返回regionlist里面所有在售房源信息。
由于链家限制，仅支持爬前100页数据，可使用GetHouseByCommunitylist。
core.GetHouseByRegionlist(city, regionlist)

#table_name: houseinfo
根据小区来爬虫在售房源房源信息，返回communitylist里面所有在售房源信息。
core.GetHouseByCommunitylist(city, communitylist)

#table_name: rentinfo
根据行政区来爬虫出租房源信息，返回regionlist里面所有出租房源信息。
由于链家限制，仅支持爬前100页数据，可使用GetRentByCommunitylist。
core.GetRentByRegionlist(city, regionlist)

#table_name: rentinfo
根据小区来爬虫出租房源信息，返回communitylist里面所有出租房源信息。
core.GetRentByCommunitylist(city, communitylist)

##table_name: sellinfo
根据小区来爬虫成交房源信息，返回communitylist里面所有成交房源信息。
部分数据无法显示因为这些数据仅在链家app显示
core.GetSellByCommunitylist(city, communitylist) 


```

## 新增[北京建委存放量房源](http://210.75.213.188/shh/portal/bjjs2016/index.aspx)信息爬虫:
+ 代码存放在[`src/jianwei`](https://github.com/niumeng07/lianjia-scrawler/blob/master/src/jianwei/jianwei.py)目录
