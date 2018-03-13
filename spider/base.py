#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 20:07:07 2018

@author: lhq
"""
import re
from time import sleep


## 延时装饰器
def delay(time=1):
    def wrapper1(func):
        def wrapper2(*args, **kwargs):
            #print("delay %s seconds" % time)
            sleep(time)
            result = func(*args, **kwargs)
            return result
        return wrapper2
    return wrapper1


class Spider:
    def __init__(self, login_session):
        self.login_session = login_session
        
    @delay(0.6)
    def get_text(self, url):
        return self.login_session.get_text(url)
    
    @delay(0.6)
    def get_json(self, url):
        return self.login_session.get_json(url)

