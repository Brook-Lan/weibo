from utils import AuthorPipeline
from spider import AuthorSpider
from login import WeiboLogin


if __name__ == "__main__":
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


