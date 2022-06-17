docker-compose -f ../docker-compose-trade.yml run --rm freqtrade download-data --exchange binance --pairs ETH/USDT --prepend --timerange 20220301-20220601 -t 30m
