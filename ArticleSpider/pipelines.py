# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
# Save Data e.g. Database
from scrapy.pipelines.images import ImagesPipeline



import mysql.connector

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok, value in results:   #results is a tuple list
            image_file_path = value['path']

        item['front_image_path'] = image_file_path

        return item
        pass

class MysqlPipeline(object):
    def __init__(self): #initialize the DB Connection
         self.conn = mysql.connector.connect(user='root', password='gmw6504192658',
                                            host='127.0.0.1', database='article_spider', charset='utf8', use_unicode=True)
         self.cursor = self.conn.cursor()  # Database operation

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title, url, create_date, fav_nums)
            VALUES (%s, %s, %s, %s)
        
        """
        self.cursor.execute(insert_sql,(item['title'],item['url'],item['create_date'],item['fav_nums']))
        self.conn.commit()
        return item

class ElasticsearchPipeline(object):
    def process_item(self, item, spider):
        item.save_to_es()
        return item


