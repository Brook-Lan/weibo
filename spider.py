#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 20:07:07 2018

@author: lhq
"""
import re
import time
from bs4 import BeautifulSoup

class Spider:
    def __init__(self, login_session):
        self.login_session = login_session
        self.url_tmp = "https://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=100606&is_search=0&visible=0&is_all=1&is_tag=0&profile_ftype=1&page={page}&pagebar={pagebar}&id={id}"
        
    def get_text(self, url):
        return self.login_session.get_text(url)
    
    def get_json(self, url):
        return self.login_session.get_json(url)
    
    def get_urls_from_id(self, id_):
        url_num = self.get_page_num(id_)
        for i in range(1, url_num+1):
            url = self.url_tmp.format(page=i, pagebar=0, id=id_)
            yield url
            for j in range(0, 2):
                url = self.url_tmp.format(page=i, pagebar=j, id=id_) + "&pre_page=%s"%i
                yield url
    
    def get_page_num(self, id_):
        para = {"page":1,
                "pagebar": 1,
                "id": id_,
                }
        url = self.url_tmp.format_map(para) + "&pre_page=1"
        d = self.get_json(url)['data']
        reg = 'countPage=(\d+)"'
        try:
            page_num = int(re.findall(reg, d, re.S)[0])
        except:
            page_num = 0
        return page_num
    
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
        
