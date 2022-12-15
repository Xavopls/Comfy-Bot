set time_start=20201117
set time_finish=20221213
set timeframes=5m 1d
set config=user_data/config_pablo_gil_wma_rsi.json


freqtrade download-data ^
 --timerange %time_start%-%time_finish% ^
 --timeframes %timeframes% ^
 --exchange binance ^
 --config %config%

freqtrade hyperopt ^
 --timerange 20201101-20221205 ^
 --hyperopt-loss SharpeHyperOptLoss ^
 --strategy Cenderawasih_3 ^
 -e 1000 ^
 --spaces buy sell ^
 --config %config%