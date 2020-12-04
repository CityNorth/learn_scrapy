import scrapy
from scrapy.http import Request
from urllib import parse
import re
import datetime
from scrapy.loader import ItemLoader

from AricelSpider.utils.common import get_md5
from AricelSpider.items import cnblogsAricelItem,ArticleItemLoader


class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['http://news.cnblogs.com']

    def parse(self, response):
        """
                1. 获取文章列表页中的文章url并交给scrapy下载后并进行解析
                2. 获取下一页的url并交给scrapy进行下载， 下载完成后交给parse
                """

        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
        post_nodes = response.css("#news_list .news_block .content")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            read_num = post_node.css(".entry_footer .view").extract_first("")
            post_url = post_node.css(".news_entry a::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url),meta={"front_image_url":image_url,
                                                                          "front_read_num":read_num},
                          callback=self.parse_detail)

        # 提取下一页并交给scrapy进行下载
        next_url = response.xpath('//*[@id="sideleft"]/div[5]/a').extract()[-1]

        if "Next" in next_url:
            next_url = response.xpath('//*[@id="sideleft"]/div[5]/a/@href').extract()[-1]
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        '''
        # 提取文章的具体字段
        front_image_url = response.meta.get('front_image_url','')
        title = response.xpath('//*[@id="news_title"]/a/text()').extract_first("")
        create_date = response.xpath('//*[@id="news_info"]/span[2]/text()').extract()[0].strip().replace("发布于","").strip()
        original_link = response.css('#link_source1::attr(href)').extract_first("")
        read_nums = response.meta.get('front_read_num','')
        match_re = re.match(".*?(\d+).*", read_nums)
        if match_re:
            read_nums = match_re.group(1)
        content = response.css("#news_body").extract_first("")

        article_item['title'] = title
        try:
            create_date = datetime.datetime.strptime(create_date, "%Y-%m-%d %H:%M").date()
        except Exception as e:
            create_date = datetime.datetime.now().date()
        article_item['create_date'] = create_date
        article_item['url'] = response.url
        article_item['url_object_id'] = get_md5(response.url)
        article_item['read_nums'] = read_nums
        article_item['content'] = content
        article_item['front_image_url'] = [front_image_url]
        article_item['original_link'] = original_link
        '''
        #通过item loader 实现
        article_item = cnblogsAricelItem()
        item_loader = ArticleItemLoader(item=cnblogsAricelItem(),response=response)

        item_loader.add_xpath('title','//*[@id="news_title"]/a/text()')
        item_loader.add_xpath('create_date','//*[@id="news_info"]/span[2]/text()')
        item_loader.add_value('url',response.url)
        item_loader.add_value('url_object_id',get_md5(response.url))
        item_loader.add_value('read_nums',response.meta.get('front_read_num',''))
        item_loader.add_css('content',"#news_body")
        item_loader.add_value('front_image_url',response.meta.get('front_image_url',''))
        item_loader.add_css('original_link','#link_source1::attr(href)')

        article_item = item_loader.load_item()

        yield article_item
