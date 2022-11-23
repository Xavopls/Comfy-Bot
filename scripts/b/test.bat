set time_start=20220601
set time_finish=20220701

if %1==bear_1 (
set time_start=20210511
set time_finish=20210720
)

if %1==bull_2 (
set time_start=20210720
set time_finish=20211110
)

set timeframes=5m
freqtrade download-data --timerange %time_start%-%time_finish% --timeframes %timeframes% --prepend --exchange binance --config user_data/config_test.json
freqtrade backtesting --timerange %time_start%-%time_finish% --strategy Bb
freqtrade plot-dataframe --timerange %time_start%-%time_finish% --config user_data/config_test.json --strategy Bb
