#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 11:31:53 2018

@author: brook
"""
import re
import json
from lxml import etree
from .base import Spider


class AuthorSpider(Spider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _authorpage_conf(self, text):
        """
        """
        def get(key):
            regexp = "\$CONFIG\['%s'\]='(.*?)'" % key
            m = re.search(regexp, text)
            if m:
                value = m.group(1)
            else:
                value = ''
            return value
        return get

    def parse_author_info(self, text):
        """从作者主页中提取作者相关的信息
        """
        conf = self._authorpage_conf(text)
        item = {}
        item['oid'] = conf('oid')
        item['page_id'] = conf('page_id')
        item['onick'] = conf('onick')
        item['domain'] = conf('domain')
        return item

    def pre_parse_authors_url(self, text):
        """预处理，从script里提取元素
        """
        text_new = json.loads(re.findall('<script>FM.view\(({.*?"domid":"Pl_Core_F4RightUserList__4",.*})\)</script>', text)[0])['html']
        return text_new

    def parse_authors_url(self, text):
        """从微博找人的分类页面中获取微博作者的主页面
        """
        text = self.pre_parse_authors_url(text)
        tree = etree.HTML(text)
        for sel in tree.xpath("//ul[@class='follow_list']/li"):
            url = sel.xpath(".//div/a[@class='S_txt1']/@href")[0]
            if url.startswith("//"):
                url = "https:" + url
            else:
                print(url)
            yield url

    def get_page_num(self, authors_text, limit=10):
        """获取作者页面的页数
        """
        text = self.pre_parse_authors_url(authors_text)
        tree = etree.HTML(text)
        page_num = tree.xpath("//div[@class='W_pages']/a[@class='page S_txt1']/text()")[-1]
        try:
            page_num = int(page_num)
        except:
            page_num = 0
        print("real_pagenum:", page_num)
        return max(int(page_num), limit) 

    def crawl(self):
        urls = ["https://d.weibo.com/1087030002_2975_5001_0",  #财经
                "https://d.weibo.com/1087030002_2975_2025_0",  # 时尚
               ]

        for url in urls:
            author_list_text = self.get_text(url)
            page_num = self.get_page_num(author_list_text)
            for i in range(1, page_num+1):
                page_url = "{pre_url}?page={page}".format(pre_url=url, page=i)
                author_list_text = self.get_text(page_url)
                for author_url in self.parse_authors_url(author_list_text):
                    author_text = self.get_text(author_url)
                    item = self.parse_author_info(author_text)
                    yield item

    
