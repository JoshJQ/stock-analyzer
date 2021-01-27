import scrapy
import pymongo
import configparser

config = configparser.ConfigParser()
config.read('../../config/config.ini')
mongo_url = config['DEFAULT']['MongoDBUrl']

dbclient = pymongo.MongoClient(mongo_url)
stock_db = dbclient["stockdb"]
stocks = stock_db["stocks"]

class PriceRatiosSpider(scrapy.Spider):
    name = 'price-ratios'

    def start_requests(self):
        baseUrl = 'https://www.macrotrends.net/stocks/charts/{}/{}/{}'
        for stock in stocks.find():
            yield scrapy.Request(url=baseUrl.format(stock['ticker'], stock['stock_name'], 'pe-ratio'), callback=self.parse_pe, meta={'stock': stock['ticker']})
            yield scrapy.Request(url=baseUrl.format(stock['ticker'], stock['stock_name'], 'price-book'), callback=self.parse_pb, meta={'stock': stock['ticker']})
            yield scrapy.Request(url=baseUrl.format(stock['ticker'], stock['stock_name'], 'roe'), callback=self.parse_roe, meta={'stock': stock['ticker']})

    def update_db(self, response, type, stock):
        table = response.xpath('//table[@class="table"]')[0]
        ratios = []
        for row in table.xpath('.//tbody/tr'):
            cols = row.xpath('.//td')
            date = cols[0].xpath('.//text()').get()
            rate = cols[2].xpath('.//text()').get()
            if type == 'roe':
                rate = cols[3].xpath('.//text()').get()
            if rate is not None and len(rate.strip()) > 0:
                ratios.append({
                    'date': date,
                    'value': rate.lstrip('$')
                })

        stocks.update_one(
            {
                'ticker': stock
            },
            {
                '$set': {
                    type: ratios
                }
            }
        )

    def parse_pe(self, response):
        self.update_db(response, 'pe', response.meta['stock'])

    def parse_pb(self, response):
        self.update_db(response, 'pb', response.meta['stock'])

    def parse_roe(self, response):
        self.update_db(response, 'roe', response.meta['stock'])
