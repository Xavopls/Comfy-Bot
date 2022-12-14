set time_start=20201117
set time_finish=20221213
set timeframes=5m 1d

::if %1==bear_1 (
::set time_start=20210511
::set time_finish=20210720
::)
::
::if %1==bull_2 (
::set time_start=20210720
::set time_finish=20211110
::)

freqtrade download-data --timerange %time_start%-%time_finish% --timeframes %timeframes% --exchange binance --config user_data/config_test.json
freqtrade backtesting --timerange %time_start%-%time_finish% --strategy Cenderawasih_3 --config user_data/config_test.json
::freqtrade plot-dataframe --timerange %time_start%-%time_finish% --strategy Cenderawasih_3 --config user_data/config_pablo_gil_wma_rsi.json
