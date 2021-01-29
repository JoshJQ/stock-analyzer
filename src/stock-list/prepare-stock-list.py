import pymongo
import configparser
import requests
import json
import time
import logging
import traceback
from pathlib import Path


def get_market_cap(stock):
    return float(stock["market_val"])


logging.basicConfig(filename='stocks-list.log', level=logging.DEBUG, format='%(asctime)s %(message)s')
config = configparser.ConfigParser()
configFile = "{0}/config/config.ini".format(str(Path.home()))
config.read(configFile)
stock_number = int(config['DEFAULT']['StockNumber'])
mongo_url = config['DEFAULT']['MongoDBUrl']

try:
    logging.info('Start to macrotrends to fetch stock list')
    response = requests.get('https://www.macrotrends.net/stocks/stock-screener')
    start_flag = 'var originalData = ['
    index_start = response.text.index(start_flag)
    index_end = response.text.index('];', index_start)
    stock_data = response.text[index_start + len(start_flag) - 1 : index_end + 1]
    stock_list = json.loads(stock_data)
    stock_list.sort(key=get_market_cap, reverse=True)
    logging.info('Fetched stock list')

    db_client = pymongo.MongoClient(mongo_url)
    stock_db = db_client["stockdb"]
    stocks = stock_db["stocks"]
    logging.info('Start to store data into database')
    count = 1
    current_date = time.strftime("%Y-%m-%d", time.localtime())
    # stock list
    for stock in stock_list:
        if stock["exchange"] in ['NYSE', 'NSDQ']:
            if count < stock_number:
                try:
                    if "." not in stock["ticker"]:
                        stocks.update_one(
                            {
                                "ticker": stock["ticker"]
                            },
                            {
                                '$set': {
                                    "stock_name": stock["comp_name"],
                                    "industry": stock["zacks_x_ind_desc"],
                                    "sector": stock["zacks_x_sector_desc"],
                                    "company_name": stock["comp_name_2"],
                                    "exchange": stock["exchange"],
                                    "market_cap": stock["market_val"],
                                    "update_date": current_date
                                }
                            },
                            upsert = True
                        )
                    count = count + 1
                except:
                    logging.error("Failed to save stock {0}".format(stock["ticker"]))
                else:
                    logging.debug("Saved stock {0}".format(stock["ticker"]))
            else:
                break
except requests.exceptions.RequestException as err:
    logging.error("Error to crawl stock list from the website: {0}".format(err))
    raise SystemExit(err)
except OSError as err:
    logging.error("OS error: {0}".format(err))
    raise SystemExit(err)
except pymongo.errors.ConnectionFailure as err:
    logging.error("Cannot connect to mongodb: {0}".format(err))
    raise SystemExit(err)
except Exception as e:
    logging.error('Unexpected exception')
    logging.error(traceback.format_exc())
    raise SystemExit(1)
else:
    logging.info('Process complete')
