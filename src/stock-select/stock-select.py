import pymongo
import datetime
import configparser
import logging
import traceback
from pathlib import Path

def get_date(stock):
    return stock["date"]

logging.basicConfig(filename='stocks-price.log', level=logging.DEBUG, format='%(asctime)s %(message)s')
config = configparser.ConfigParser()
configFile = "{0}/config/config.ini".format(str(Path.home()))
config.read(configFile)
mongo_url = config['DEFAULT']['MongoDBUrl']

try:
    dbclient = pymongo.MongoClient(mongo_url)
    stock_db = dbclient["stockdb"]
    stocks = stock_db["stocks"]

    selected_stocks = []
    for stock in stocks.find({"prices": {"$exists": True}, "pb": {"$exists": True}, "pe": {"$exists": True}}):
        prices = stock['prices']
        prices.sort(key=get_date, reverse=True)
        pe_rank = 0
        pb_rank = 0
        begin_date = (datetime.datetime.now() - datetime.timedelta(days = 3650)).strftime('%Y-%m-%d')

        latest_pe = prices[0]['pe']
        latest_pb = prices[0]['pb']
        if latest_pe == 0 or latest_pb == 0:
            continue
        count = 1
        for price in prices[1:]:
            if (price['date'] < begin_date):
                break
            if (latest_pe > price['pe']):
                pe_rank = pe_rank + 1
            if (latest_pb > price['pb']):
                pb_rank = pb_rank + 1
            count = count + 1
        pe_rank_percent = pe_rank / count
        pb_rank_percent = pb_rank / count
        if pe_rank_percent < 0.5 and pb_rank_percent < 0.2:
            selected_stocks.append({
                'stock_name': stock['stock_name'],
                'ticker': stock['ticker'],
                'company_name': stock['company_name'],
                'industry': stock['industry'],
                'market_cap': stock['market_cap'],
                'pe_rank': pe_rank_percent,
                'pb_rank': pb_rank_percent,
                'roe': stock['roe']
            })

    roe_begin_date = (datetime.datetime.now() - datetime.timedelta(days = 365 * 5)).strftime('%Y-%m-%d')
    results = []
    for stock in selected_stocks:
        roes = stock['roe']
        roes.sort(key=get_date, reverse=True)
        roe_match = True
        for roe in stock['roe']:
            if roe['date'] < roe_begin_date:
                break;
            historical_roe = roe['value'].rstrip('%')
            if float(historical_roe) < 15:
                print('Stock ', stock['stock_name'], ' ROE Not match')
                roe_match = False
                break

        if roe_match == True:
            results.append({
                'stock_name': stock['stock_name'],
                            'ticker': stock['ticker'],
                'company_name': stock['company_name'],
                'industry': stock['industry'],
                'market_cap': stock['market_cap'],
                'pe_rank': stock['pe_rank'],
                'pb_rank': stock['pb_rank']
            })

    print('***********************************************************************************************************')
    with open("stocks_result.csv", "w") as outfile:
        outfile.write('stock_name, ticker, company_name, industry, market_cap, pe_rank, pb_rank')
        for stock in results:
            outfile.write('{}, {}, {}, {}, {}, {}, {}'.format(stock['stock_name'], stock['ticker'], stock['company_name'],
                                                    stock['industry'], stock['market_cap'], stock['pe_rank'], stock['pb_rank']))

except pymongo.errors.ConnectionFailure as err:
    logging.error("Cannot connect to mongodb: {0}".format(err))
    raise SystemExit(err)
except IOError as err:
    logging.error("Failed to write file: {0}".format(err))
    raise SystemExit(err)
except Exception as e:
    logging.error('Unexpected exception')
    logging.error(traceback.format_exc())
    raise SystemExit(1)
else:
    logging.info('Process complete')