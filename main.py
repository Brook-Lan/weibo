from utils import AuthorPipeline, WeiboPipeline
from spider import AuthorSpider, WeiboSpider, WeiboSpider2
#from spider.weibo import WeiboSpider2
from login import WeiboLogin

def crawl_author():
    mongo_url = "localhost"
    mongo_db = "weibo"
    mongo_coll = "author"

    account = input("enter your weibo account:\n")
    pwd = input("enter your passwords:\n")
    login = WeiboLogin(account, pwd)
    sp = AuthorSpider(login)
    with AuthorPipeline(mongo_url, mongo_db, mongo_coll) as pipe:
        for item in sp.crawl():
            pipe.save(item)
            
            
def crawl_weibo(start=0, width=300):
    with open("weibo_ids.csv") as f:
        ids = f.readlines()
    ids = [s.strip().strip('"') for s in ids[1:]]
    
    account = input("enter your weibo account:\n")
    pwd = input("enter your passwords:\n")
    lg = WeiboLogin(account, pwd)
    sp = WeiboSpider2(lg)
    
    mongo_url = "localhost"
    mongo_db = "weibo"
    mongo_coll = "posts_newfields"
    
    id_ = "1006062557129567"
    with WeiboPipeline(mongo_url, mongo_db, mongo_coll) as pipe:
        for i, id_ in enumerate(ids[:start+width]):
            print(i)
            if i < start:
                continue           
            for item in sp.crawl(id_, "2015-01-01 00:00"):
                pipe.update(item)
        


if __name__ == "__main__":
    crawl_weibo(start=44)



