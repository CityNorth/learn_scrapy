# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi

import codecs
import json
import pymysql
import pymysql.cursors

class AricelspiderPipeline:
    def process_item(self, item, spider):
        return item

#保存json文件
class JsonWithEncodingPipline(object):
    def __init__(self):
        self.file = codecs.open("article.json","w+",encoding= "utf-8")
    def process_item(self,item,spider):
        item['create_date'] = str(item['create_date'])
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item
    def spider_close(self,spider):
        self.file.close()

#调用scrapy提供的json export导出json文件
class JsonExporterPipleline(object):
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

# 采用同步的机制写入mysql
class MysqlPipeline(object):
    def __init__(self):
        self.coon = pymysql.connect(host='localhost', user='root', password='123456', port=3306, db='spider',charset="utf8",use_unicode=True)
        self.cursor = self.coon.cursor()

    def process_item(self,item,spider):
        insert_sql = '''
            INSERT INTO cnblogs(title,url,url_object_id,read_nums)
            VALUES (%s,%s,%s,%s)
        '''
        self.cursor.execute(insert_sql,(item['title'],item['url'],item['url_object_id'],item['read_nums']))
        self.coon.commit()
        return item


class MysqlTwistedPipline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            password = settings["MYSQL_PASSWORD"],
            charset = 'utf8',
            cursorclass = pymysql.cursors.DictCursor,
            use_unicode = True,
        )
        dbpool = adbapi.ConnectionPool("pymysql", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql = '''
            INSERT INTO cnblogs(title,url,url_object_id,read_nums)
            VALUES (%s,%s,%s,%s)
        '''
        cursor.execute(insert_sql,(item['title'],item['url'],item['url_object_id'],item['read_nums']))

#获取图片路径
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path
        return item