### 新浪微博爬虫

- AuthorSpider: 爬取微博用户作者的id信息

- WeiboSpider: 根据作者id爬取微博内容(用BeautifulSoup解析网页)

- WeiboSpider2，继承自WeiboSpider， 采用xpath(lxml.etree)解析网页

  结果均保存在mongodb

### Requirements:

```
python3
requests
pymongo
BeautifulSoup
lxml
```

