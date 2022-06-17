import numpy as np
import pandas as pd
from pandas import DataFrame

from freqtrade.strategy.interface import IStrategy

import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class Bolinger(IStrategy):
    
    
   
    INTERFACE_VERSION = 2

    stoploss = -0.01
    trailing_stop = True

  
    trailing_stop = False
    
    timeframe = '1m'

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
        
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_lowerband'] = bollinger['lower']
        dataframe['bb_middleband'] = bollinger['mid']
        dataframe['bb_upperband'] = bollinger['upper']
        dataframe['rsi'] = ta.RSI(dataframe)

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['close'].shift(1)<dataframe['bb_lowerband']) & 
		        (dataframe['close'] > dataframe['bb_lowerband']) &
		        (dataframe['rsi'] < 50)
            ),
            'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        
        return dataframe
