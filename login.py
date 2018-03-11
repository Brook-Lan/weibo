#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 20:07:07 2018

@author: lhq
"""
import re
import urllib
import base64
import binascii
import rsa
import requests

class WeiboLogin:
    def __init__(self, nick, pwd):
        headers = {'User-Agent' : 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)'}
        self._session = requests.Session()
        self._session.headers.update(headers)
        self.pre_log(nick, pwd)
        
    
    def pre_log(self, nick, pwd):
        prelogin_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.15)&_=1400822309846' % nick 
        loginfo = self.get_text(prelogin_url)
        ## following info will be used on login request as post datas
        servertime = re.findall('"servertime":(.*?),' , loginfo)[0]
        pubkey = re.findall('"pubkey":"(.*?)",' , loginfo)[0]
        rsakv = re.findall('"rsakv":"(.*?)",' , loginfo)[0]
        nonce = re.findall('"nonce":"(.*?)",' , loginfo)[0]

        su = base64.b64encode(bytes(urllib.request.quote(nick) , encoding = 'utf-8'))
        rsaPublickey = int(pubkey , 16)
        key = rsa.PublicKey(rsaPublickey , 65537)
        
        message = bytes(str(servertime) + '\t' + str(nonce) + '\n' + str(pwd) , encoding = 'utf-8')
        sp = binascii.b2a_hex(rsa.encrypt(message , key))    
        
        datas = {'entry': 'weibo',
                 'gateway': 1,
                 'from': '',
                 'savestate': 7,
                 'useticket': 1,
                 'pagerefer': 'http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D',
                 'vsnf': 1,
                 'su': su,
                 'service': 'miniblog',
                 'servertime': servertime,
                 'nonce': nonce,
                 'pwencode': 'rsa2',
                 'rsakv': rsakv,
                 'sp': sp,
                 'sr': '1680*1050' ,
                 'encoding': 'UTF-8',
                 'prelt': 961,
                 'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack'
                 }
        res = self._session.post('http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)' , data=datas)
        urll = re.findall("location.replace\(\'(.*?)\'\);" , res.text)[0]
        self.get_text(urll)
    
    def get_response(self, url):
        res = self._session.get(url)
        return res
    
    def get_text(self, url):
        res = self.get_response(url)
        return res.text
    
    def get_json(self, url):
        res = self.get_response(url)
        return res.json()
        

