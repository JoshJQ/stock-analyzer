# stock-analyzer
A set of python scripts to fetch stock data from internet and analyze the stocks with low prices

Package to be installed:
pip install requests
pip install pymongo
pip install dnspython
pip install scrapy

Commands to run:

1. Get stock list
cd stock-list
python prepare-stock-list.py

2. Crawl stock price ratios
cd stockRatios
scrapy crawl price-ratios --logfile stock-ratios.log