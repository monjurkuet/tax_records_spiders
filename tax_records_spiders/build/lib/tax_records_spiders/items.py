# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class UpdateTaxRecordsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    owner = scrapy.Field()
    owner_first = scrapy.Field()
    owner_middle = scrapy.Field()
    owner_last = scrapy.Field()
    owner_suffix = scrapy.Field()
    owner_nickname = scrapy.Field()
    parcel_id = scrapy.Field()
    tax_id = scrapy.Field()
    geo_code = scrapy.Field()
    state = scrapy.Field()
    county = scrapy.Field()
    mailing_address = scrapy.Field()
    mailing_address_line_1 = scrapy.Field()
    mailing_address_line_2 = scrapy.Field()
    mailing_address_city = scrapy.Field()
    mailing_address_state = scrapy.Field()
    mailing_address_postal_code = scrapy.Field()
    property_address = scrapy.Field()
    property_address_line_1 = scrapy.Field()
    property_address_line_2 = scrapy.Field()
    property_address_city = scrapy.Field()
    property_address_state = scrapy.Field()
    property_address_postal_code = scrapy.Field()

    table = scrapy.Field()


