#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient

class MongoPipeline:
    query_fields = None  ## for update method
    def __init__(self, mongo_url, db_name, coll_name):
        self.client = MongoClient(mongo_url)
        db = self.client.get_database(db_name)
        self.coll = db.get_collection(coll_name)

    def close(self):
        self.client.close()

    def save(self, item):
#        query = {k:v for k,v in item.items() if k in self.query_fields}
#        try:
#            self.coll.update_one(query, {"$set":item}, upsert=True)
#        except:
#            self.close()
        self.insert(item)
            
    def update(self, item):
        query = {k:v for k,v in item.items() if k in self.query_fields}
        try:
            self.coll.update_one(query, {"$set":item}, upsert=True)
        except:
            self.close()
    
    def insert(self, item):
        try:
            self.coll.insert_one(item)
        except:
            self.close()   
            
    def find(self, *args, **kwargs):
        return self.coll.find(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, type, value, trace):
        self.close()

class AuthorPipeline(MongoPipeline):
    query_fields = ("oid", )


class WeiboPipeline(MongoPipeline):
	query_fields = "pub_time author post".split()
