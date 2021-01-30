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

2. Crawl stock ratios
cd stockRatios
scrapy crawl price-ratios --logfile stock-ratios.log

3. Fetch stock prices
cd stock-price
python prepare-stock-price.py

4. Calculate PE and PB
cd stock-calculate
python stock-calculate.py

5. Select the stocks with low prices
cd stock-select
python stock-select.py