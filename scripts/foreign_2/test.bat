set time_start=20201117
set time_finish=20221213
set timeframes=5m 1d

::freqtrade download-data --timerange %time_start%-%time_finish% --timeframes %timeframes% --exchange binance --config user_data/config_foreign_backtest.json
freqtrade backtesting --timerange %time_start%-%time_finish% --strategy Foreign2 --config user_data/config_foreign_backtest.json
::freqtrade plot-dataframe --timerange %time_start%-%time_finish% --strategy Cenderawasih_3 --config user_data/config_pablo_gil_wma_rsi.json
