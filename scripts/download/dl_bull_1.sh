rm ../../user_data/data/binance/futures/ETH_USDT-30m-futures.json
docker-compose -f ../../docker-compose-trade.yml run --rm freqtrade download-data --exchange binance --pairs ETH/USDT --prepend --timerange 20200906-20210514 -t 30m
