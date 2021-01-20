# -*- coding: utf-8 -*-
from __future__ import print_function

import datetime

import peewee

import settings

if settings.DBENGINE.lower() == 'mysql':
    database = peewee.MySQLDatabase(
        settings.DBNAME,
        host=settings.DBHOST,
        port=settings.DBPORT,
        user=settings.DBUSER,
        passwd=settings.DBPASSWORD,
        charset='utf8',
        use_unicode=True,
    )

elif settings.DBENGINE.lower() == 'sqlite3':
    database = peewee.SqliteDatabase(settings.DBNAME)

elif settings.DBENGINE.lower() == 'postgresql':
    database = peewee.PostgresqlDatabase(
        settings.DBNAME,
        user=settings.DBUSER,
        password=settings.DBPASSWORD,
        host=settings.DBHOST,
        charset='utf8',
        use_unicode=True,
    )

else:
    raise AttributeError("Please setup datatbase at settings.py")


class BaseModel(peewee.Model):

    class Meta:
        database = database


class Community(BaseModel):
    id = peewee.BigIntegerField(primary_key=True)
    title = peewee.CharField()
    link = peewee.CharField(unique=True)
    district = peewee.CharField()
    bizcircle = peewee.CharField()
    tagList = peewee.CharField()
    onsale = peewee.CharField()
    onrent = peewee.CharField(null=True)
    year = peewee.CharField(null=True)
    housetype = peewee.CharField(null=True)
    cost = peewee.CharField(null=True)
    service = peewee.CharField(null=True)
    company = peewee.CharField(null=True)
    building_num = peewee.CharField(null=True)
    house_num = peewee.CharField(null=True)
    price = peewee.CharField(null=True)
    city = peewee.CharField(null=True)
    validdate = peewee.DateTimeField(default=datetime.datetime.now)


class Houseinfo(BaseModel):
    houseID = peewee.CharField(primary_key=True)
    title = peewee.CharField()
    link = peewee.CharField()
    community = peewee.CharField()
    years = peewee.CharField()
    housetype = peewee.CharField()
    square = peewee.CharField()
    direction = peewee.CharField()
    floor = peewee.CharField()
    taxtype = peewee.CharField()
    totalPrice = peewee.CharField()
    unitPrice = peewee.CharField()
    followInfo = peewee.CharField()
    decoration = peewee.CharField()
    towertype = peewee.CharField()
    business = peewee.CharField()
    validdate = peewee.DateTimeField(default=datetime.datetime.now)


class Hisprice(BaseModel):
    houseID = peewee.CharField()
    totalPrice = peewee.CharField()
    date = peewee.DateTimeField(default=datetime.datetime.now)

    class Meta:
        primary_key = peewee.CompositeKey('houseID', 'totalPrice')


class Sellinfo(BaseModel):
    houseID = peewee.CharField(primary_key=True)
    title = peewee.CharField()
    link = peewee.CharField()
    community = peewee.CharField()
    years = peewee.CharField()
    housetype = peewee.CharField()
    square = peewee.CharField()
    direction = peewee.CharField()
    floor = peewee.CharField()
    status = peewee.CharField()
    source = peewee.CharField()
    totalPrice = peewee.CharField()
    unitPrice = peewee.CharField()
    dealdate = peewee.CharField(null=True)
    dealinfo = peewee.CharField()
    updatedate = peewee.DateTimeField(default=datetime.datetime.now)


class Rentinfo(BaseModel):
    houseID = peewee.CharField(primary_key=True)
    title = peewee.CharField()
    link = peewee.CharField()
    region = peewee.CharField()
    zone = peewee.CharField()
    meters = peewee.CharField()
    other = peewee.CharField()
    subway = peewee.CharField()
    decoration = peewee.CharField()
    heating = peewee.CharField()
    price = peewee.CharField()
    pricepre = peewee.CharField()
    updatedate = peewee.DateTimeField(default=datetime.datetime.now)


def database_init():
    database.connect()
    database.create_tables(
        [Community, Houseinfo, Hisprice, Sellinfo, Rentinfo], safe=True)
    database.close()
