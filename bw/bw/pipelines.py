# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import os
from urllib import request
from scrapy.pipelines.images import ImagesPipeline
from . import settings

class BwPipeline:
    def process_item(self, item, spider):
        return item

class BwImagesPipeline(ImagesPipeline):#继承父类ImagesPipeline
    def get_media_requests(self, item, info):#重写父类方法
        request_objs = super(BwImagesPipeline,self).get_media_requests(item,info)
        for request_obj in request_objs:
            request_obj.item = item
        return request_objs
    def file_path(self, request, response=None, info=None):
        path = super(BwImagesPipeline,self).file_path(request,response,info)
        title = request.item.get("title")
        images_store = settings.IMAGES_STORE
        title_path = os.path.join(images_store,title)
        if not os.path.exists(title_path):
            os.mkdir(title_path)
        image_name = path.replace("full/","")
        image_path = os.path.join(title_path,image_name)
        return image_path