set time_start=20220701
set time_finish=20220801
set timeframes=5m
freqtrade backtesting --timerange %time_start%-%time_finish% --strategy Bb
