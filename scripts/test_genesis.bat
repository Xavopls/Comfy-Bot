set time_start=20210101
set time_finish=20220101
freqtrade download-data --timerange=%time_start%-%time_finish% --prepend --exchange binance --config user_data/config_test.json
freqtrade backtesting --timerange=%time_start%-%time_finish% --strategy Genesis
freqtrade plot-dataframe --timerange=%time_start%-%time_finish% --config user_data/config_test.json --strategy Genesis
