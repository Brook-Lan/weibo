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
    account = input("enter your weibo account:\n")
    pwd = input("enter your passwords:\n")
    lg = WeiboLogin(account, pwd)
    sp = WeiboSpider(lg)
    
    id_ = "1006062557129567"
    
    from utils import MongoPipeline
    mongo_url = "192.168.2.126"
    mongo_db = "test"
    mongo_coll = "weibo_new"
    
    with MongoPipeline(mongo_url, mongo_db, mongo_coll) as pipe:
        for item in sp.crawl(id_):
            pipe.save(item)    


if __name__ == "__main__":
    crawl_weibo()



