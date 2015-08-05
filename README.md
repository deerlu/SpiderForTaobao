# SpiderForTaobao

By [鹿迪](https://github.com/deerlu).


## Description
**SpiderForTaobao** 是一个基于[Scrapy](https://github.com/scrapy/scrapy)的爬虫程序，它能够根据指定关键字和指定的宝贝数量爬取淘宝网站上的宝贝成交记录。

## Usage

在终端输入如下命令，以采用默认参数，关键字为deerlu，所需获取的宝贝数量为5：

```console
scrapy crawl taobao
```

或输入如下命令，以设置关键字和需获取的宝贝数量：

```console
scrapy crawl taobao -a keyword="XXX" -a count=X
```

您也可以根据scrapy的用法来指定输出格式，例如：

```console
scrapy crawl taobao -a keyword="XXX" -a count=X -o items.json
```

Scrapy的具体用法请见[Scrapy在线文档](http://doc.scrapy.org/en/latest/)

## Requirements

* Scrapy 1.0.1
* Python 2.7
* Works on Mac OSX

## Authors

* 鹿迪 (https://github.com/deerlu)


## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request
