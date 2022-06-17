import numpy as np
import pandas as pd
from pandas import DataFrame

from freqtrade.strategy.interface import IStrategy

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class Geremain(IStrategy):

    minimal_roi = {
        "60": 0.01,
        "30": 0.02,
        "0": 0.04
    }
   
    INTERFACE_VERSION = 2

    stoploss = -0.10
  
    trailing_stop = False
    
    timeframe = '15m'

    process_only_new_candles = False

    use_sell_signal = False
    sell_profit_only = False
    ignore_roi_if_buy_signal = False

    startup_candle_count: int = 0

    order_types = {
        'buy': 'limit',
        'sell': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    order_time_in_force = {
        'buy': 'gtc',
        'sell': 'gtc'
    }

    plot_config = {
        'main_plot': {
        },
        'subplots': {
            "volumeAverage": {
                'volumeAverage': {'color': 'orange'},
            },
            "EMA": {
                'ema13red': {'color': 'red'},
                'ema34yellow': {'color': 'yellow'},
            }
        }
    }

    def informative_pairs(self):
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        dataframe['ema13red'] = ta.EMA(dataframe, timeperiod=13)
        dataframe['ema34yellow'] = ta.EMA(dataframe, timeperiod=34)
        dataframe['volumeAverage'] = ta.SMA(dataframe['volume'], timeperiod=20)

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['ema13red'] > dataframe['ema34yellow']) &
                (dataframe['ema13red'].shift(1) < dataframe['ema34yellow'].shift(1)) &    
                (dataframe['volume'] >= dataframe['volumeAverage'])
            ),
            'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['ema13red'] < dataframe['ema34yellow']) &
                (dataframe['ema13red'].shift(1) > dataframe['ema34yellow'].shift(1))
            ),
            'sell'] = 1
        return dataframe
