import logging

DBENGINE = 'mysql'  # ENGINE OPTIONS: mysql, sqlite3, postgresql
DBNAME = 'ershoufang'
DBUSER = 'root'
DBPASSWORD = ''
DBHOST = '127.0.0.1'
DBPORT = 3306
CITY = 'bj'  # only one, shanghai=sh shenzhen=sh......
REGIONLIST = [u'chaoyang', u'haidian', u'changping', u'shunyi', u'dongcheng', u'xicheng', u'daxing', u'fangshan', u'tongzhou', u'fengtai']  # only pinyin support
# REGIONLIST = [u'changping', u'shunyi']  # only pinyin support
CoreNums = 2
ThreadNums = 2

logging.basicConfig(format='[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s', level=logging.INFO)
