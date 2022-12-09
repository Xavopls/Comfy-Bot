set time_start=20201101
set time_finish=20221129
set timeframes=30m

freqtrade download-data --timerange %time_start%-%time_finish% --timeframes %timeframes% --exchange binance --config user_data/config_scotty.json
freqtrade hyperopt --config user_data/config_scotty.json --timerange 20201101-20221205 --hyperopt-loss SharpeHyperOptLoss --strategy Scotty -e 2000 --spaces buy sell --config user_data/config_scotty.json