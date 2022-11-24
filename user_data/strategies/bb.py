# ToDo:

# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
from functools import reduce
from json import load
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame, notnull
import time
from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IStrategy, IntParameter, informative, merge_informative_pair)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
from datetime import datetime, timedelta, time
from freqtrade.persistence import Trade
from freqtrade.exchange import timeframe_to_prev_date


# This class is a sample. Feel free to customize it.
class Bb(IStrategy):
    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Can this strategy go short?
    can_short: bool = False
    stoploss = -0.1

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        "0": 0.30,
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    use_custom_stoploss = True

    # Trailing stoploss
    # trailing_stop = True
    # trailing_stop_positive = 0.231
    # trailing_stop_positive_offset = 0.286
    # trailing_only_offset_is_reached = False

    # Optimal timeframe for the strategy.
    timeframe = '5m'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Hyperoptable parameters
    # todo: change vwap session start time to 13:30 utc
    buy_above_vwap = BooleanParameter(default=False, space="buy", optimize=True)
    buy_us_market_hours = BooleanParameter(default=False, space="buy", optimize=True)
    buy_only_weekdays = BooleanParameter(default=False, space="buy", optimize=True)
    buy_tp_sl_ratio = DecimalParameter(low=1.0, high=3.0, decimals=1,
                                       default=2.0, space='buy', optimize=True, load=True)

    sell_support_margin_percentage = DecimalParameter(low=0.92, high=1.00, decimals=2,
                                                      default=1.0, space='sell', optimize=True, load=True)

    @property
    def protections(self):
        prot = []
        return prot

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 240

    # Optional order type mapping.
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # Optional order time in force.
    order_time_in_force = {
        'entry': 'gtc',
        'exit': 'gtc'
    }

    plot_config = {
        'main_plot': {
            'ema12': {'color': 'red'},
            'vwap': {'color': 'yellow'},
            'support': {'color': 'purple'},

        },
        'subplots': {
            'wt': {
                'wt1': {'color': 'red'},
                'wt2': {'color': 'blue'},
            },
            'RSI': {
                'rsi': {'color': 'purple'},
            }

        }
    }

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        # get access to all pairs available in whitelist.
        # pairs = self.dp.current_whitelist()
        # Assign tf to each pair, so they can be downloaded and cached for strategy.
        # informative_pairs = [(pair, '5m') for pair in pairs]
        # informative_pairs = [("ETH/USDT", "5m")]

        # return informative_pairs

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame

        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        :param dataframe: Dataframe with data from the exchange
        :param metadata: Additional information, like the currently traded pair
        :return: a Dataframe with all mandatory indicators for the strategies
        """

        # dataframe = self.custom_session(dataframe, start='09:30', end='16:00')
        dataframe['vwap'] = self.custom_vwap(dataframe, '01:00')
        dataframe = self.create_supports(dataframe, '01:00')
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['ema12'] = ta.EMA(dataframe, timeperiod=12)
        dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)
        dataframe['hlc3'] = (dataframe['high'] + dataframe['low'] + dataframe['close']) / 3
        esa = ta.EMA(dataframe['hlc3'], 9)
        de = ta.EMA(abs(dataframe['hlc3'] - esa), 9)
        ci = (dataframe['hlc3'] - esa) / (0.015 * de)
        dataframe['day_of_week'] = dataframe['date'].dt.day_name()
        dataframe['wt1'] = ta.EMA(ci, 12)
        dataframe['wt2'] = ta.SMA(dataframe['wt1'], 3)

        return dataframe

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                        current_rate: float, current_profit: float, **kwargs) -> float:
        """
        Custom stoploss logic, returning the new distance relative to current_rate (as ratio).
        e.g. returning -0.05 would create a stoploss 5% below current_rate.
        The custom stoploss can never be below self.stoploss, which serves as a hard maximum loss.

        For full documentation please go to https://www.freqtrade.io/en/latest/strategy-advanced/

        When not implemented by a strategy, returns the initial stoploss value
        Only called when use_custom_stoploss is set to True.

        :param pair: Pair that's currently analyzed
        :param trade: trade object.
        :param current_time: datetime object, containing the current datetime
        :param current_rate: Rate, calculated based on pricing settings in exit_pricing.
        :param current_profit: Current profit (as ratio), calculated based on current_rate.
        :param **kwargs: Ensure to keep this here so updates to this won't break your strategy.
        :return float: New stoploss value, relative to the current rate
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)

        trade_date = timeframe_to_prev_date(self.timeframe, trade.open_date_utc)
        trade_candle = dataframe.loc[dataframe['date'] == trade_date]
        if not trade_candle.empty:
            trade_candle = trade_candle.squeeze()
            stoploss_price = trade_candle['support']
            stoploss_price = stoploss_price * self.sell_support_margin_percentage.value
            if stoploss_price < current_rate:
                return (stoploss_price / current_rate) - 1
        return 1

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with entry columns populated
        """

        # dataframe.loc[
        #     (
        #             (dataframe['high'] < dataframe['vwap']) &
        #             (dataframe['wt1'] < 0) &
        #             (dataframe['wt2'] < 0) &
        #             (qtpylib.crossed_above(dataframe['close'], dataframe['ema12'])) &
        #
        #             # Volume not 0
        #             (dataframe['volume'] > 0)
        #     ),
        #     ['enter_long', 'enter_tag']] = (1, 'buy_signal')

        ########################### START HYPEROPT ###########################
        conditions = []

        conditions.append(dataframe['wt1'] < 0)
        conditions.append(dataframe['wt2'] < 0)
        conditions.append(qtpylib.crossed_above(dataframe['close'], dataframe['ema12']))
        conditions.append((dataframe['volume'] > 0))

        # Volume not 0
        conditions.append(dataframe['volume'] > 0)

        if not self.buy_above_vwap.value:
            conditions.append(dataframe['high'] < dataframe['vwap'])

        if self.buy_us_market_hours.value:
            conditions.append(dataframe['time'] >= '13:30')
            conditions.append(dataframe['time'] <= '20:00')

        if self.buy_only_weekdays.value:
            conditions.append(dataframe['day_of_week'] != 'Saturday')
            conditions.append(dataframe['day_of_week'] != 'Sunday')

        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                ['enter_long', 'enter_tag']] = (1, 'buy_signal')
        ########################### END HYPEROPT ###########################

        return dataframe

    def custom_exit(self, pair: str, trade: Trade, current_time: datetime, current_rate: float,
                    current_profit: float, **kwargs):
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        sl_tp_ratio = self.buy_tp_sl_ratio.value
        sell_condition = current_rate >= (trade.open_rate + sl_tp_ratio * (trade.open_rate - trade.stop_loss))
        if trade.enter_tag == 'buy_signal' and sell_condition:
            return 'sell_signal'
        return None

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the exit signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with exit columns populated
        """

        dataframe.loc[
            (
            ),

            ['exit_long', 'exit_tag']] = (1, 'exit_1')

        return dataframe

    # Support methods

    def custom_session(self, df: DataFrame, start, end):
        """
        :param df: DataFrame
        :param start: String
        :param end: String
        remove previous globex day from df

        """
        df['time'] = df['date'].dt.strftime('%H:%M')
        df['volume_session'] = np.where((df['time'] <= start) | (df['time'] >= end), 0, df['volume'])
        df['high_session'] = np.where((df['time'] <= start) | (df['time'] >= end), 0, df['high'])
        df['close_session'] = np.where((df['time'] <= start) | (df['time'] >= end), 0, df['close'])
        df['low_session'] = np.where((df['time'] <= start) | (df['time'] >= end), 0, df['low'])
        df['open_session'] = np.where((df['time'] <= start) | (df['time'] >= end), 0, df['open'])

        return df.copy()

    def custom_vwap(self, df, reset_time):
        df['time'] = df['date'].dt.strftime('%H:%M')
        df['reset_time'] = np.where((df['time'] == time), 1, 0)

        typical = ((df['high'] + df['low'] + df['close']) / 3).values
        volume = df['volume'].values

        tpv = self.reset_cumsum(df=df, serie=(typical * volume), reset_time=reset_time)
        cum_vol = self.reset_cumsum(df=df, serie=volume, reset_time=reset_time)

        return pd.Series(index=df.index,
                         data=tpv / cum_vol)

    def reset_cumsum(self, df, serie, reset_time):
        """
        Given a serie and a df, it cumsums it and resets the sum at the given time.
        Returns a serie.
        """
        df['tmp_data'] = serie
        time = df['date'].dt.strftime('%H:%M')
        df['reset_time'] = np.where((time == reset_time), 1, 0)
        df['cumsum'] = df['reset_time'].cumsum()
        res = df.groupby(df['cumsum'])['tmp_data'].cumsum()
        return res

    def create_supports(self, df, reset_time):
        # Hardcoded... Sorry.
        df['reset'] = np.where((df['time'] == '01:00') |
                               (df['time'] == '04:20') |
                               (df['time'] == '07:40') |
                               (df['time'] == '11:00') |
                               (df['time'] == '14:20') |
                               (df['time'] == '17:40') |
                               (df['time'] == '21:00') |
                               (df['time'] == '00:20'), 1, 0)
        df['cumsum'] = df['reset'].cumsum()
        df['support'] = df.groupby('cumsum')['low'].transform('min')

        return df
