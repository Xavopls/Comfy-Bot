TIME_START=20210101
TIME_FINISH=20220601
TIMEFRAME=15m

freqtrade download-data --timerange $TIME_START-$TIME_FINISH --timeframes $TIMEFRAME --exchange binance --config user_data/config_pablito.json
freqtrade hyperopt --config user_data/config_pablito.json --timerange $TIME_START-$TIME_FINISH --hyperopt-loss SortinoHyperOptLoss --strategy Pablito -e 1000 --spaces buy sell
