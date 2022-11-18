set time_start=20221025
set time_finish=20221030
set timeframes=5m
freqtrade backtesting --timerange %time_start%-%time_finish% --strategy Moisture
