#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@create Time:2018-03-13

@author:Brook
"""
import re
import time
from datetime import datetime

from lxml import etree
from bs4 import BeautifulSoup

from spider.base import Spider
from login import WeiboLogin


class WeiboUrl:
    """
    独立出来的url生成类，根据id生成爬取的url	
    """
    def __init__(self):
        self.tmplate = "https://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain={domain}&is_search=0&visible=0&is_all=1&is_tag=0&profile_ftype=1&page={page}&pagebar={pagebar}&id={id}"
        
    def pagenums_url_of_id(self, id_):
        """返回的url用来获取用户微博的帖子页码数
        """
        para = {"page":1,
                "pagebar":1,
                "id": id_,
                "domain": id_[:6]
        }
        url = self.tmplate.format_map(para) + "&pre_page=1"
        return url
    
    def contentpage_url_of_id(self, id_, page_nums):
        """根据id生成微博内容的url
        """
        for page in range(1, page_nums+1):
            url = self.tmplate.format(page=page, pagebar=0, id=id_, domain=id_[:6])
            yield url
            for j in range(0, 2):
                url = self.tmplate.format(page=page, pagebar=j, id=id_, domain=id_[:6]) + "&pre_page=%s"%page
                yield url
                

class WeiboSpider(Spider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.urlgen = WeiboUrl()
        
    def get_page_nums(self, id_):
        """获取微博页码数
        """
        url = self.urlgen.pagenums_url_of_id(id_)
        d = self.get_json(url)['data']
        reg = "countPage=(\d+)"
        try:
            page_num = int(re.findall(reg, d, re.S)[0])
        except:
            page_num = 0
        return page_num
    
    def get_urls(self, id_):
        """根据id获取微博的所有url
        """
        page_nums = self.get_page_nums(id_)
        for url in self.urlgen.contentpage_url_of_id(id_, page_nums):
            yield url
            
    def parse(self, json_data):
        text = json_data['data']
        soup = BeautifulSoup("<html><head></head><body>" + text + "</body></html>", "lxml")
        reg = '<em>(\d+)</em>'
        tmp = soup.find_all("div", attrs={"class": "WB_detail"})
        tmp2 = soup.find_all("div", attrs={"class":"WB_handle"})
        if len(tmp) > 0 :
            for i in range(len(tmp)):
                item = {}
                item["author"] = tmp[i].find("div", attrs={"class": "WB_info"}).find("a").get_text()
                item["post"] = tmp[i].find("div", attrs={"class": "WB_text W_f14"}).get_text().replace("\n", "").replace(" ","").replace( "\u200b", "")

                # -*- 爬取发布时间 -*-
                item["pub_time"] = tmp[i].find("a", attrs={"class": "S_txt2"}).get("title")

                # -*- 爬取转发数 -*-
                if re.findall(reg,str(tmp2[i].find("span", attrs={"class": "line S_line1","node-type":"forward_btn_text"})), re.S):
                    item["transfer_num"] = int(re.findall(reg,str(tmp2[i].find("span", attrs={"class": "line S_line1","node-type":"forward_btn_text"})), re.S)[0])
                else:
                    item["transfer_num"] = 0

                # -*- 爬取评论数 -*-
                if re.findall(reg, str(tmp2[i].find("span", attrs={"class": "line S_line1", "node-type": "comment_btn_text"})), re.S):
                    item["comment_num"] = int(re.findall(reg, str(tmp2[i].find("span", attrs={"class": "line S_line1", "node-type": "comment_btn_text"})), re.S)[0])
                else:
                    item["comment_num"] = 0

                # -*- 爬取点赞数 -*-
                if re.findall(reg, str(tmp2[i].find("span", attrs={"node-type": "like_status"})), re.S):
                    item["like_num"] = int(re.findall(reg, str(tmp2[i].find("span", attrs={"node-type": "like_status"})), re.S)[0])
                else:
                    item["like_num"] = 0
                item["crawl_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                yield item
                
    def crawl(self, id_, limit_date=None):
        """爬虫启动方法
        """
        if limit_date is None:
            limit_date = "2010-01-01 01:00"
        for url in self.get_urls(id_):
            print(url)
            d = self.get_json(url)
            for item in self.parse(d):
                yield item
            if item['pub_time'] < limit_date:
                break
            


def to_digit(str_):
    m = re.search("\d+", str_)
    if m:
        return int(m.group())
    else:
        return 0


class WeiboSpider2(WeiboSpider):
    """该爬虫用xpath取代BeautifulSoup提取网页元素，提取的字段稍有改动，其他无区别
    """
    def parse(self, json_data):
        text = json_data['data']
        tree = etree.HTML(text.replace('\u200b', ""))
        tmp_tree = tree.xpath("//div[@mid]")
        for sel in tmp_tree:
            item = {}
            try:
                item['author'] = sel.xpath(".//div[@class='WB_info']/a[@usercard]/text()")[0]
            except:
                continue
            tmp_id = sel.xpath(".//div[@class='WB_info']/a[@usercard]/@usercard")[0]
            item['author_id'] = re.findall("id=(\d+)", tmp_id)[0]
            item['pub_time'] = sel.xpath(".//div/a[@date]/@title")[0]
            item['pub_from'] = "".join(sel.xpath(".//div/a[@class='S_txt2' and @action-type]/text()"))
            item['post'] = "".join([s.strip() for s in sel.xpath(".//div[@class='WB_detail']/div[contains(@class, 'WB_text') and @nick-name]/text()")])
            item['transfer_num'] = to_digit(sel.xpath(".//div[@class='WB_handle']//span[@class='line S_line1' and @node-type='forward_btn_text']//em/text()")[-1])
            item['comment_num'] = to_digit(sel.xpath(".//div[@class='WB_handle']//span[@class='line S_line1' and @node-type='comment_btn_text']//em/text()")[-1])
            item['like_num'] = to_digit(sel.xpath(".//div[@class='WB_handle']//span[@node-type='like_status']//em/text()")[-1])
            
            item['crawl_time'] = datetime.now()
            yield item

