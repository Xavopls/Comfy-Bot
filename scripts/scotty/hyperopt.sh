TIME_START=20201101
TIME_FINISH=20221129
TIMEFRAME=30m

freqtrade download-data --timerange $TIME_START-$TIME_FINISH --timeframes $TIMEFRAME --exchange binance --config user_data/config_scotty.json
freqtrade hyperopt --config user_data/config_scotty.json --timerange $TIME_START-$TIME_FINISH --hyperopt-loss SharpeHyperOptLoss --strategy Scotty -e 1000 --spaces buy sell