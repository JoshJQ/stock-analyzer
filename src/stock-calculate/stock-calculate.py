import pymongo
import logging
import configparser
import traceback
from pathlib import Path

def get_date(data):
    return data['date']

logging.basicConfig(filename='stocks-calculate.log', level=logging.DEBUG, format='%(asctime)s %(message)s')
config = configparser.ConfigParser()
configFile = "{0}/config/config.ini".format(str(Path.home()))
config.read(configFile)
mongo_url = config['DEFAULT']['MongoDBUrl']

try:
    dbclient = pymongo.MongoClient(mongo_url)
    stock_db = dbclient["stockdb"]
    stocks = stock_db["stocks"]
    for stock in stocks.find({"prices": {"$exists": True}, "pb": {"$exists": True}, "pe": {"$exists": True}}).batch_size(20):
        prices = stock['prices']
        pes = stock['pe']
        pbs = stock['pb']
        prices.sort(key=get_date, reverse=True)
        pes.sort(key=get_date, reverse=True)
        pbs.sort(key=get_date, reverse=True)
        results = []
        i = 0
        j = 0
        for price in prices:
            pe = 0
            pb = 0
            while i < len(pes) and price['date'] < pes[i]['date']:
                i = i + 1
            if i < len(pes) and pes[i]['value'] != 0:
                earning = float(pes[i]['value'].replace(',', ''))
                if earning > 0:
                    pe = float(price['close'].replace(',', '')) / earning

            while j < len(pbs) and price['date'] < pbs[j]['date']:
                j = j + 1
            if j < len(pbs) and pbs[j]['value'] != 0:
                book_value = float(pbs[j]['value'].replace(',', ''))
                if book_value > 0:
                    pb = float(price['close'].replace(',', '')) / book_value

            results.append({
                'date': price['date'],
                'open': price['open'],
                'high': price['high'],
                'low': price['low'],
                'close': price['close'],
                'volume': price['volume'],
                'pe': pe,
                'pb': pb
            })

        stocks.update_one(
            {
                'ticker': stock["ticker"]
            },
            {
                '$set': {
                    "prices": results
                }
            }
        )
except pymongo.errors.ConnectionFailure as err:
    logging.error("Cannot connect to mongodb: {0}".format(err))
    raise SystemExit(err)
except Exception as e:
    logging.error('Unexpected exception')
    logging.error(traceback.format_exc())
    raise SystemExit(1)
else:
    logging.info('Process complete')