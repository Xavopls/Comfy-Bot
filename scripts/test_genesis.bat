set timerange=20220901
freqtrade backtesting --timerange=%timerange%- --strategy Genesis
freqtrade plot-dataframe --timerange=%timerange%- --config user_data/config.json --strategy Genesis
