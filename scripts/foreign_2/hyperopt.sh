TIME_START=20201117
TIME_FINISH=20221213
TIMEFRAME=5m 1h
CONFIG=user_data/config_pablo_gil_wma_rsi.json


freqtrade download-data \
  --timerange $TIME_START-$TIME_FINISH \
  --timeframes $TIMEFRAME \
  --exchange binance \
  --config $CONFIG

freqtrade hyperopt \
  --config $CONFIG \
  --timerange $TIME_START-$TIME_FINISH \
  --hyperopt-loss SharpeHyperOptLoss \
  --strategy Cenderawasih_3 \
  -e 1000 \
  --spaces buy sell
