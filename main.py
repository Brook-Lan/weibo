from utils import AuthorPipeline
from spider import AuthorSpider
from spider.weibo import WeiboSpider
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
            
            
def crawl_weibo():
    with open("weibo_ids.csv") as f:
        ids = f.readlines()
    ids = [s.strip().strip('"') for s in ids[1:]]
    
    account = input("enter your weibo account:\n")
    pwd = input("enter your passwords:\n")
    lg = WeiboLogin(account, pwd)
    sp = WeiboSpider(lg)
    
    from utils import WeiboPipeline
    mongo_url = "localhost"
    mongo_db = "weibo"
    mongo_coll = "posts"
    
    
    id_ = "1006062557129567"
    with WeiboPipeline(mongo_url, mongo_db, mongo_coll) as pipe:
        for id_ in ids[:100]:
            for item in sp.crawl(id_, "2014-01-01 00:00"):
                pipe.update(item)
        


if __name__ == "__main__":
    crawl_weibo()



