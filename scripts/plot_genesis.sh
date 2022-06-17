docker-compose -f ../docker-compose-trade.yml down
docker-compose -f ../docker-compose-plot.yml up -d
docker-compose -f ../docker-compose-plot.yml run --rm freqtrade backtesting --strategy Genesis --timeframe 30m
docker-compose -f ../docker-compose-plot.yml run --rm freqtrade plot-dataframe -p ETH/USDT --strategy Genesis
