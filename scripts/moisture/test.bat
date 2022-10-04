set time_start=20220915
set time_finish=20220930
set timeframes=1m
freqtrade download-data --timerange %time_start%-%time_finish% --timeframes %timeframes% --prepend --exchange binance --config user_data/config_test.json
freqtrade backtesting --timerange %time_start%-%time_finish% --strategy Moisture
freqtrade plot-dataframe --timerange %time_start%-%time_finish% --config user_data/config_test.json --strategy Moisture
