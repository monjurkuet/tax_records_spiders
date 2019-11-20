# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class UpdateTaxRecordsPipeline(object):
    def process_item(self, item, spider):
        # pass
        # print('I am in the pipeline ' + item['table'])
        # if item.get('table'):
        #     item['table'] = 'My value has been changed in pipleline'
        #
        #     return item
        #
        # item['table']
        return item
