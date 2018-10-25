# -*- coding: utf-8 -*-
import scrapy
import datetime
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
from scrapy.loader import ItemLoader



from ArticleSpider.utils.common import get_md5

import re


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts']

    def parse(self, response):

        '''Get url lists, let scrapy download and analysis, then get next page url, download and parse'''


        post_urls = response.css('a.archive-title::attr(href)').extract()

        #without front_page_image
        #for post_url in post_urls:
            #yield Request(url=post_url, callback= self.parse_detail())
        #    yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse_detail)
        #   print(post_url)

        #post_nodes = response.css('.post-thumb a')
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css('img::attr(src)').extract_first()
            post_url = post_node.css('::attr(href)').extract_first()
            yield Request(url=parse.urljoin(response.url, post_url), meta={'front_image_url': image_url},
                          callback=self.parse_detail, dont_filter=True)

        next_url = response.css('.next.page-numbers::attr(href)').extract_first('')
        if next_url:
            #yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse_detail)  #just one page
            yield Request(url=next_url, callback=self.parse)  #generate real all websites

    def parse_detail(self, response):

        article_item = JobBoleArticleItem()

        # Extract information inside each page
        # using css to extract


        #------------------ 1 xpath scrapy -----------------
        #re_selector = response.xpath('//*[@id="post-114168"]/div[1]/h1/text()') #different page maybe different id
        #re_selector2 = response.xpath('//div[@class="entry-header"]//h1/text()')

        # ------------------ 2 css scrapy ------------------------

        front_image_url = response.meta.get('front_image_url', '')  #no error front page image
        title = response.css(".entry-header h1::text").extract()[0]  #IndexError: list index out of range for some page
        create_date = response.css('p.entry-meta-hide-on-mobile::text').extract()[0].strip()[0:10]

        praise_nums = response.css('.vote-post-up h10::text').extract()[0]

        fav_nums_str = response.css('.bookmark-btn::text').extract()[0]
        #match_re = re.match('.*(\d+).*', fav_nums_str)
        #if match_re:
        #    fav_nums_2 = match_re.group(1)
        length2 = len(fav_nums_str)
        if len(fav_nums_str) > 4:
            fav_nums= int(fav_nums_str[1:len(fav_nums_str)-3])
        else:
            fav_nums= 0

        comment_nums_str = response.css("a[href='#article-comment'] span::text").extract()[0]
        length = len(comment_nums_str)
        if len(comment_nums_str) > 4:
            comment_nums = int(comment_nums_str[1:len(comment_nums_str)-3])
        else:
            comment_nums = 0

        content = response.css('div.entry').extract_first('')

        tag_list = response.css('p.entry-meta-hide-on-mobile a::text').extract()
        tag_list = [element for element in tag_list if not element.strip().endswith("评论")] #get rid of words in tag line

        tags = ','.join(tag_list)


        article_item["url_object_id"] = get_md5(response.url)
        article_item["title"] = title
        article_item["url"] = response.url
        try:
            create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
        except Exception as e:
            create_date = datetime.datetime.now().date()
        article_item["create_date"] = create_date
        article_item["front_image_url"] = [front_image_url]
        article_item["praise_nums"] = praise_nums
        article_item["comment_nums"] = comment_nums
        article_item["fav_nums"] = fav_nums
        article_item["tags"] = tags
        article_item["content"] = content


        #item loader load into items
        '''

        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))

        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("fav_nums", ".bookmark-btn::text")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", "div.entry")
        article_item = item_loader.load_item()
        '''


        yield article_item  # pass to item
        pass
