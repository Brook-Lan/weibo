#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@create Time:2018-03-13

@author:Brook
"""
import re
import time

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
                item["nickname"] = tmp[i].find("div", attrs={"class": "WB_info"}).find("a").get_text()
                item["Post"] = tmp[i].find("div", attrs={"class": "WB_text W_f14"}).get_text().replace("\n", "").replace(" ","").replace( "\u200b", "")

                # -*- 爬取发布时间 -*-
                item["Pubtime"] = tmp[i].find("a", attrs={"class": "S_txt2"}).get("title")

                # -*- 爬取转发数 -*-
                if re.findall(reg,str(tmp2[i].find("span", attrs={"class": "line S_line1","node-type":"forward_btn_text"})), re.S):
                    item["Transfer_num"] = int(re.findall(reg,str(tmp2[i].find("span", attrs={"class": "line S_line1","node-type":"forward_btn_text"})), re.S)[0])
                else:
                    item["Transfer_num"] = 0

                # -*- 爬取评论数 -*-
                if re.findall(reg, str(tmp2[i].find("span", attrs={"class": "line S_line1", "node-type": "comment_btn_text"})), re.S):
                    item["Comment_num"] = int(re.findall(reg, str(tmp2[i].find("span", attrs={"class": "line S_line1", "node-type": "comment_btn_text"})), re.S)[0])
                else:
                    item["Comment_num"] = 0

                # -*- 爬取点赞数 -*-
                if re.findall(reg, str(tmp2[i].find("span", attrs={"node-type": "like_status"})), re.S):
                    item["Like_num"] = int(re.findall(reg, str(tmp2[i].find("span", attrs={"node-type": "like_status"})), re.S)[0])
                else:
                    item["Like_num"] = 0
                item["Scraltime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
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
            if item['Pubtime'] < limit_date:
                break
            
