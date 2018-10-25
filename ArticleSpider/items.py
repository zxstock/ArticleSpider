# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import datetime
import re

import scrapy
import redis
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,TakeFirst, Join

from ArticleSpider.models.es_types import ArticleType
from w3lib.html import remove_tags

from elasticsearch_dsl.connections import connections
es = connections.create_connection(ArticleType._doc_type.using)

redis_cli = redis.StrictRedis(host="localhost")

class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

def gen_suggests(index,info_tuple):
    #generate search suggest array according to input string
    used_words = set() # deduplicate
    #get rid of duplicate in other positions, e.g. in Title and Text both same word, weight first will not be changed
    suggests = []
    for text, weight in info_tuple:
        if text:
            # use es analyzer port to analyze string text (len>1), split into words and up/low transform
            words = es.indices.analyze(index=index, analyzer='ik_max_word', params={'filter':['lowercase']},body=text)
            analyzed_words = set([r['token'] for r in words['tokens'] if len(r['token'])>1])
            new_words = analyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({'input':list(new_words),'weight':weight})

    return suggests

class ArticleItemLoader(ItemLoader):
    default_input_processor = TakeFirst()

def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()

    except Exception as e:

        create_date = datetime.datetime.now().date()
        return create_date

def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums

def remove_comment_tags(value):
    if "评论" in value:
        return ""
    else:
        return value

def return_value(value):
    return value




class JobBoleArticleItem(scrapy.Item):  #like dict
    title = scrapy.Field()
    create_date = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()  #md5 for long url
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()  #upgrade in pipiline and settings
    praise_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    fav_nums = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()




    def save_to_es(self):
        article = ArticleType()
        article.title = self['title']
        article.create_date = self['create_date']
        article.content = remove_tags(self['content'])
        article.front_image_url = self['front_image_url']
        if 'front_image_path' in self:
            article.front_image_path = self['front_image_path']
        article.praise_nums = self['praise_nums']
        article.fav_nums = self['fav_nums']
        article.comment_nums = self['comment_nums']
        article.url = self['url']
        article.tags = self['tags']
        article.meta.id = self['url_object_id']

        article.suggest = gen_suggests(ArticleType._doc_type.index, ((article.title,10),(article.tags,7)))

        #article.suggest = gen_suggests(ArticleType._doc_type.index,((article.title,10),(article.tags,7)))

        article.save()  #save into elastics search after called in pipelines
        #全局变量 redis and then test
        redis_cli.incr("jobbole_count") #automatic +1 from 1

        return

