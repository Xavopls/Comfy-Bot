set time_start=20221022
set time_finish=20221129
set timeframes=30m

if %1==bear_1 (
set time_start=20210511
set time_finish=20210720
)

if %1==bull_2 (
set time_start=20210720
set time_finish=20211110
)

freqtrade download-data --timerange %time_start%-%time_finish% --timeframes %timeframes% --exchange binance --config user_data/config_scotty.json
freqtrade backtesting --timerange %time_start%-%time_finish% --strategy Scotty --config user_data/config_scotty.json
freqtrade plot-dataframe --timerange %time_start%-%time_finish% --strategy Scotty --config user_data/config_scotty.json
