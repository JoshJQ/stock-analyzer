# stock-analyzer
Stock analyzer consists of a set of python scripts to grab the data for the stocks from the internet and find out the appropriate stocks to buy. All the data will be stored to Mongodb Atlas service.
The scripts will run in the following flow:
* Prepare stock list - prepare-stock-list.py
The script will fetch a list of 500 stocks from website https://www.macrotrends.net. Only the stocks with market value less than 100 billions will be captured. The information below is also grabbed for each stock.
    * Stock ticker - instrument identifier
    * Stock name
    * Industry
    * Sector
    * Company name
    * Stock exchange
    * Market value
 * Crawl stock ratios
 The script will leverage with scrapy crawler framework to crawl the following key ratios from https://www.macrotrends.net.
    * Earning per share
    * Book value per share
    * Return on equity
 * Fetch stock prices
 The script will fetch the historical prices for the stocks by calling public API from https://www.alphavantage.co. The API is free to have 500 calls per day.
 * Calculate PE and PB
 With all the ratios and prices from previous steps, this script will calculate all the historical PE and PB for the stocks.
 * Select the stocks
 The stocks which can match with following criteria will be selected.
    * PE is less than 50% ranking in the past 10 years
    * PB is less than 20% ranking in the pass 10 years
    * ROE is more than 15%
 
# Prerequisites to run
* Python3
* Packages to be installed:
    * pip install requests
    * pip install pymongo
    * pip install dnspython
    * pip install scrapy
* MongoDB

# How to run:
Make sure configuration file config.ini is updated properly and run the scripts in the following sequence.
* Get stock list
    * cd stock-list
    * python prepare-stock-list.py

* Crawl stock ratios
    * cd stockRatios
    * scrapy crawl price-ratios --logfile stock-ratios.log

* Fetch stock prices
    * cd stock-price
    * python prepare-stock-price.py

* Calculate PE and PB
    * cd stock-calculate
    * python stock-calculate.py

* Select the stocks with low prices
    cd stock-select
    python stock-select.py