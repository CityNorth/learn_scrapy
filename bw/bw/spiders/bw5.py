import scrapy
from bw.items import BwItem
import logging

logger = logging.getLogger(__name__)

class Bw5Spider(scrapy.Spider):
    name = 'bw5'
    allowed_domains = ['car.autohome.com.cn']
    start_urls = ['https://car.autohome.com.cn/pic/series/65.html']

    def parse(self, response):
        uiboxs = response.xpath("//div[@class='uibox']")[1:]
        for uibox in uiboxs:
            title = uibox.xpath(".//div[@class='uibox-title']/a/text()").get()
            urls = uibox.xpath(".//div[@class='uibox-con carpic-list03']/ul/li/a/img/@src").getall()
            # for x in urls:
            #     url = response.urljoin(x)
            #     print(url)
            # 获取所有图片url
            urls = list(map(lambda url: response.urljoin(url), urls))
            item = BwItem(title=title, image_urls=urls)
            logger.warning(item)
            yield item
