set time_start=20221101
set time_finish=20221110
set timeframes=5m
freqtrade download-data --timerange %time_start%-%time_finish% --timeframes %timeframes% --prepend --exchange binance --config user_data/config_test.json
freqtrade backtesting --timerange %time_start%-%time_finish% --strategy Bb
freqtrade plot-dataframe --timerange %time_start%-%time_finish% --config user_data/config_test.json --strategy Bb
