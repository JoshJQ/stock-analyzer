import pymongo
import datetime
import requests
import time
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
apiKey = config['DEFAULT']['ApiKey']

try:
    dbclient = pymongo.MongoClient(mongo_url)
    stock_db = dbclient["stockdb"]
    stocks = stock_db["stocks"]

    base_url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={0}&apikey={1}"
    for stock in stocks.find().batch_size(20):
        if stock["ticker"].find('.') == -1:
            logging.info("Processing prices for stock {0}".format(stock["ticker"]))
            prices = []
            if "prices" in stock:
                prices = stock["prices"]
            stock_url = base_url.format(stock["ticker"], apiKey)
            latest_date = '1900-01-01'
            if prices is not None and len(prices) > 0:
                prices.sort(key=get_date, reverse=True)
                latest_date = prices[0]["date"]
                trade_date = datetime.datetime.strptime(latest_date, '%Y-%m-%d')
                delta_date = datetime.datetime.now() - trade_date
                # Miss over 100 days' trade, fetch full data
                if delta_date.days > 100:
                    stock_url = stock_url + '&outputsize=full'
                elif delta_date.days < 5:
                    logging.info("Stock {0} has been fetched within 5 days, ignore it".format(stock["ticker"]))
                    continue
            else:
                stock_url = stock_url + '&outputsize=full'
                prices = []

            response = requests.get(stock_url)
            if "Time Series (Daily)" in response.json():
                prices_data = response.json()["Time Series (Daily)"]
                for key in prices_data.keys():
                    if key > latest_date:
                        prices.append({
                            "date": key,
                            "open": prices_data[key]["1. open"],
                            "high": prices_data[key]["2. high"],
                            "low": prices_data[key]["3. low"],
                            "close": prices_data[key]["4. close"],
                            "volume": prices_data[key]["5. volume"]
                        })
                    else:
                        break

                prices.sort(key=get_date, reverse=True)
                logging.info("prices size: {0}".format(len(prices)))
                try:
                    stocks.update_one(
                        {
                            'ticker': stock["ticker"]
                        },
                        {
                            '$set': {
                                "prices": prices
                            }
                        }
                    )
                except:
                    logging.error("Failed to save stock {0}".format(stock["ticker"]))
                else:
                    logging.debug("Saved stock {0}".format(stock["ticker"]))
            time.sleep(13)
except requests.exceptions.RequestException as err:
    logging.error("Error to crawl stock price from the website: {0}".format(err))
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
