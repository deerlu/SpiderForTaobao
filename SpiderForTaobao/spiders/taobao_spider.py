# -*- coding:utf-8 -*-
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request
import json, re
from SpiderForTaobao.items import SpiderfortaobaoItem

class TaobaoSpider(Spider):
	name = "taobao"
	allowed_domains = ['www.taobao.com','item.taobao.com','detailskip.taobao.com','s.taobao.com']

	headers = {
		"Accept": "*/*",
		"Accept-Encoding": "gzip, deflate",
		"Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
		"Connection": "keep-alive",
		"Host": "detailskip.taobao.com",
		"Referer": "https://item.taobao.com/item.htm?spm=a230r.1.14.1.bNjCbf&id=18072477194&ns=1&abbucket=10",
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:36.0) Gecko/20100101 Firefox/36.0"
	} 

	# 可以使用-a keyword="xxx" -a count=xxx 来指定搜索关键字及要获取的宝贝数量
	def __init__(self, keyword="deerlu", count=5, *args, **kwargs):
		super(TaobaoSpider, self).__init__(*args, **kwargs)
		self.keyword = keyword #搜索关键字
		self.count = count #需要得到的宝贝数量

	# 在www.taobao.com搜索keyword指定的关键字，爬取并创建request对象
	def start_requests(self):
		url = "https://s.taobao.com/search?q=%s&imgfile=&commend=all&ssid=s5-e&search_type=item&sourceId=tb.index&spm=a21bo.7724922.8452-taobao-item.2&initiative_id=tbindexz_20150802" % self.keyword
		return [Request(url, callback=self.get_first_page_products)]

	# 获取搜索结果列表第一页里的所有宝贝，如果小于要获取的宝贝数量，则调用get_rest_of_pages_products以获取足够的宝贝；否则调用parse_every_product对每个宝贝进行处理
	def get_first_page_products(self, response):
		for sel in response.xpath('//script'):
			if "g_page_config = " in sel.extract():
				jsonStr =  sel.re(r"g_page_config\s=\s.*;")[0][16:-1]
				jsonData = json.loads(jsonStr)
				# 将该页的所有宝贝id添加到idList中
				idList = jsonData["mainInfo"]["traceInfo"]["traceData"]["allNids"]
				# 搜索到的宝贝总数量
				totalProducts = jsonData["mainInfo"]["traceInfo"]["traceData"]["totalHits"]
				# 搜索结果总页数
				totalPage = jsonData["mods"]["sortbar"]["data"]["pager"]["totalPage"]
				# 当前页数
				currentPage = jsonData["mods"]["sortbar"]["data"]["pager"]["currentPage"]
				break

		
		# 如果搜索到的总宝贝数比要获取的宝贝数量少，则修改要获取的宝贝数量为总宝贝数
		if int(totalProducts) < int(self.count):
			self.count = totalProducts

		if len(idList) >= int(self.count):
			# 调用parse_every_product对self.count个宝贝进行处理
			for id in idList[0:int(self.count)]:
				url = "https://item.taobao.com/item.htm?spm=a230r.1.14.1.bNjCbf&id=%s&ns=1&abbucket=10#detail" % id
				item = SpiderfortaobaoItem()
				#存储该宝贝id到item中
				item["productId"] = id
				item["dealRecords"] = []
				yield Request(url,meta={'item': item},callback=self.parse_every_product)
		elif int(currentPage) < int(totalPage):
			# 获取下一页的宝贝
			currentPage = currentPage + 1
			dateVal =(currentPage - 1) * 44
			url = "https://s.taobao.com/search?data-key=s&data-value=%s&ajax=true&_ksTS=1438785627718_769&callback=jsonp770&ie=utf8&initiative_id=staobaoz_20150805&stats_click=search_radio_all%%3A1&js=1&imgfile=&q=%%E7%%A8%%8B%%E5%%BA%%8F%%E4%%BB%%A3%%E5%%86%%99&suggest=history_4&_input_charset=utf-8&wq=&suggest_query=&source=suggest&bcoffset=4" % dateVal
			yield Request(url,meta={'idList': idList, 'totalPage': totalPage, 'currentPage': currentPage},callback=self.get_rest_of_pages_products)

	# 获取剩下若干页的宝贝
	def get_rest_of_pages_products(self, response):
		idList = response.meta['idList']
		totalPage = response.meta['totalPage']
		currentPage = response.meta['currentPage']

		jsonStr = response.body[ response.body.index("(") + 1 : response.body.rindex(")") ]
		jsonData = json.loads(jsonStr)
		# 将该页的所有宝贝id添加到idList中
		idList.extend(jsonData["mainInfo"]["traceInfo"]["traceData"]["allNids"])

		while(len(idList) < int(self.count) and int(currentPage) < int(totalPage)):
			# 获取下一页的宝贝
			currentPage = currentPage + 1
			dateVal =(currentPage - 1) * 44
			url = "https://s.taobao.com/search?data-key=s&data-value=%s&ajax=true&_ksTS=1438785627718_769&callback=jsonp770&ie=utf8&initiative_id=staobaoz_20150805&stats_click=search_radio_all%%3A1&js=1&imgfile=&q=%%E7%%A8%%8B%%E5%%BA%%8F%%E4%%BB%%A3%%E5%%86%%99&suggest=history_4&_input_charset=utf-8&wq=&suggest_query=&source=suggest&bcoffset=4" % dateVal
			yield Request(url,meta={'idList': idList, 'totalPage': totalPage, 'currentPage': currentPage},callback=self.get_rest_of_pages_products)

		for id in idList[0:int(self.count)]:
			# 调用parse_every_product对self.count个宝贝进行处理
			url = "https://item.taobao.com/item.htm?spm=a230r.1.14.1.bNjCbf&id=%s&ns=1&abbucket=10#detail" % id
			item = SpiderfortaobaoItem()
			#存储该宝贝id到item中
			item["productId"] = id
			item["dealRecords"] = []
			yield Request(url,meta={'item': item},callback=self.parse_every_product)

	
	# 针对每个宝贝，获取其所有成交记录
	def parse_every_product(self, response):
		for sel in response.xpath('//script'):
			if "g_config.recordsApi=" in sel.extract():
				p = re.compile(r'g_config\.recordsApi=.*;')
				m = p.search(sel.extract())
				if m:
					# 获取宝贝的成交记录链接
					dealRecordsUrl = m.group()[21:-2]
				else:
					print "Not found g_config.recordsApi"
				break

		item = response.meta['item']
		# 获取该宝贝的标题
		item["title"] = response.xpath('//title/text()').extract()[0]
		url = 'https:%s&bid_page=1' % dealRecordsUrl
		yield Request(url,headers = self.headers,meta={'item': item, 'dealRecordsUrl': dealRecordsUrl},callback=self.get_all_records)

	def get_all_records(self,response):
		jsonData = json.loads(response.body)
		# 判断是否有下一页成交记录
		hasNext = jsonData["data"]["showBuyerList"]["hasNext"]
		# 当前正在处理的成交记录页数
		currentRecordPage = jsonData["data"]["showBuyerList"]["currentPage"]

		dealRecordsUrl = response.meta["dealRecordsUrl"]
		item = response.meta["item"]

		for data in jsonData["data"]["showBuyerList"]["data"]:
			strTmp = "%s %s %d %s %s" % (data["buyerNick"], data["price"], data["amount"], data["payTime"], data["skuInfo"][0])
			# 将每条成交记录的详细信息存入item中
			item["dealRecords"].append(strTmp)

		#处理下一页
		if hasNext:
			url = 'https:%s&bid_page=%d' % (dealRecordsUrl, currentRecordPage + 1)
			yield Request(url,headers = self.headers,meta={'item': item, 'dealRecordsUrl': dealRecordsUrl},callback=self.get_all_records)
		else:
			yield item
		