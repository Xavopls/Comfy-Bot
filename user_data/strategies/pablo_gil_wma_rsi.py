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
from typing import Optional

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
from datetime import datetime, timedelta, time
from freqtrade.persistence import Trade
from freqtrade.exchange import timeframe_to_prev_date


# This class is a sample. Feel free to customize it.
class PabloGilWmaRsi(IStrategy):
    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Can this strategy go short?
    can_short: bool = False
    stoploss = -0.9

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        "0": 0.90,
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    use_custom_stoploss = True
    position_adjustment_enable = True

    # Optimal timeframe for the strategy.
    timeframe = '30m'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # Trailing stop:
    trailing_stop = False
    trailing_stop_positive = 0.348
    trailing_stop_positive_offset = 0.371
    trailing_only_offset_is_reached = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Hyperoptable parameters
    buy_us_market_hours = BooleanParameter(default=False, space="buy", optimize=True)
    buy_only_weekdays = BooleanParameter(default=False, space="buy", optimize=True)
    buy_rsi_value = IntParameter(low=20, high=40, default=40, space='buy', optimize=True)
    buy_rsi_lookback_candles = IntParameter(low=2, high=5, default=3, space='buy', optimize=True)
    buy_wma_grow_older = BooleanParameter(default=False, space="buy", optimize=True)

    sell_rsi_value = IntParameter(low=60, high=80, default=60, space='sell', optimize=True)
    sell_rsi_lookback_candles = IntParameter(low=2, high=5, default=3, space='sell', optimize=True)
    sell_wma_grow_older = BooleanParameter(default=False, space="sell", optimize=True)
    sell_resize_position = BooleanParameter(default=True, space="sell", optimize=True)

    sell_resize_position_ratio = DecimalParameter(low=0.5, high=2, decimals=1,
                                                  default=1.5, space='sell', optimize=True)

    sell_resize_profit_amount = DecimalParameter(low=1.5, high=3, decimals=1,
                                                 default=1.5, space='sell', optimize=True)

    sell_support_margin_percentage = DecimalParameter(low=0.95, high=1.00, decimals=2,
                                                      default=1.0, space='sell', optimize=True)
    sell_exit_ratio = DecimalParameter(low=1.6, high=3, decimals=1,
                                       default=2, space='sell', optimize=True)

    @property
    def protections(self):
        prot = []
        return prot

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 10

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
            'vwap': {'color': 'yellow'},
            'support': {'color': 'purple'},
        },
        'subplots': {
            'stoch_fast': {
                'fastd': {'color': 'red'},
                'fastk': {'color': 'blue'},
                'zero': {'color': 'black'},
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

        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds different TA indicators to the given DataFrame

        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        :param dataframe: Dataframe with data from the exchange
        :param metadata: Additional information, like the currently traded pair
        :return: a Dataframe with all mandatory indicators for the strategies
        """
        dataframe['day_of_week'] = dataframe['date'].dt.day_name()
        dataframe['wma14'] = ta.WMA(dataframe, timeperiod=14)
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe = self.create_supports(dataframe)

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
            stoploss_price = trade_candle['support'] * self.sell_support_margin_percentage.value
            if stoploss_price < current_rate:
                return (stoploss_price / current_rate) - 1
        return 1

    def adjust_trade_position(self, trade: Trade, current_time: datetime,
                              current_rate: float, current_profit: float,
                              min_stake: Optional[float], max_stake: float,
                              current_entry_rate: float, current_exit_rate: float,
                              current_entry_profit: float, current_exit_profit: float,
                              **kwargs) -> Optional[float]:
        """
        Custom trade adjustment logic, returning the stake amount that a trade should be
        increased or decreased.
        This means extra buy or sell orders with additional fees.
        Only called when `position_adjustment_enable` is set to True.

        For full documentation please go to https://www.freqtrade.io/en/latest/strategy-advanced/

        When not implemented by a strategy, returns None

        :param trade: trade object.
        :param current_time: datetime object, containing the current datetime
        :param current_rate: Current buy rate.
        :param current_profit: Current profit (as ratio), calculated based on current_rate.
        :param min_stake: Minimal stake size allowed by exchange (for both entries and exits)
        :param max_stake: Maximum stake allowed (either through balance, or by exchange limits).
        :param current_entry_rate: Current rate using entry pricing.
        :param current_exit_rate: Current rate using exit pricing.
        :param current_entry_profit: Current profit using entry pricing.
        :param current_exit_profit: Current profit using exit pricing.
        :param **kwargs: Ensure to keep this here so updates to this won't break your strategy.
        :return float: Stake amount to adjust your trade,
                       Positive values to increase position, Negative values to decrease position.
                       Return None for no action.
        """
        # SL / TP ratio to resize the position
        if self.sell_resize_position.value:
            # Price to resize
            resize_position_rate = (
                    trade.open_rate + self.sell_resize_position_ratio.value * (trade.open_rate - trade.stop_loss))

            if current_rate >= resize_position_rate and trade.nr_of_successful_exits == 0:
                return -(trade.stake_amount / self.sell_resize_profit_amount.value)

        return None

    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                            proposed_stake: float, min_stake: Optional[float], max_stake: float,
                            leverage: float, entry_tag: Optional[str], side: str,
                            **kwargs) -> float:

        dataframe, _ = self.dp.get_analyzed_dataframe(pair=pair, timeframe=self.timeframe)
        current_candle = dataframe.iloc[-1].squeeze()

        sl_percentage = (current_rate / current_candle['support'] - 1) * 100

        # Case where SL < 1%. We can't leverage, so we can't reach 1%.
        sized_stake = proposed_stake

        # Max drawdown = 1%
        if sl_percentage >= 1:
            sized_stake = proposed_stake / sl_percentage

        return sized_stake

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with entry columns populated
        """
        conditions = []

        conditions.append((dataframe['wma14']).shift(1) < dataframe['wma14'])

        if self.buy_wma_grow_older.value:
            conditions.append((dataframe['wma14']).shift(2) < dataframe['wma14'].shift(1))

        if self.buy_rsi_lookback_candles.value == 2:
            conditions.append(
                (qtpylib.crossed_above(dataframe['rsi'].shift(1), self.buy_rsi_value.value)) |
                (qtpylib.crossed_above(dataframe['rsi'].shift(2), self.buy_rsi_value.value))
            )
        if self.buy_rsi_lookback_candles.value == 3:
            conditions.append(
                (qtpylib.crossed_above(dataframe['rsi'].shift(1), self.buy_rsi_value.value)) |
                (qtpylib.crossed_above(dataframe['rsi'].shift(2), self.buy_rsi_value.value)) |
                (qtpylib.crossed_above(dataframe['rsi'].shift(3), self.buy_rsi_value.value))
            )
        if self.buy_rsi_lookback_candles.value == 4:
            conditions.append(
                (qtpylib.crossed_above(dataframe['rsi'].shift(1), self.buy_rsi_value.value)) |
                (qtpylib.crossed_above(dataframe['rsi'].shift(2), self.buy_rsi_value.value)) |
                (qtpylib.crossed_above(dataframe['rsi'].shift(3), self.buy_rsi_value.value)) |
                (qtpylib.crossed_above(dataframe['rsi'].shift(4), self.buy_rsi_value.value))
            )
        if self.buy_rsi_lookback_candles.value == 5:
            conditions.append(
                (qtpylib.crossed_above(dataframe['rsi'].shift(1), self.buy_rsi_value.value)) |
                (qtpylib.crossed_above(dataframe['rsi'].shift(2), self.buy_rsi_value.value)) |
                (qtpylib.crossed_above(dataframe['rsi'].shift(3), self.buy_rsi_value.value)) |
                (qtpylib.crossed_above(dataframe['rsi'].shift(4), self.buy_rsi_value.value)) |
                (qtpylib.crossed_above(dataframe['rsi'].shift(5), self.buy_rsi_value.value))
            )

        # US Market timeframe
        if self.buy_us_market_hours.value:
            conditions.append(dataframe['time'] >= '13:30')
            conditions.append(dataframe['time'] <= '20:00')

        # No trading on weekends
        if self.buy_only_weekdays.value:
            conditions.append(dataframe['day_of_week'] != 'Saturday')
            conditions.append(dataframe['day_of_week'] != 'Sunday')

        # Volume not 0
        conditions.append(dataframe['volume'] > 0)

        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                ['enter_long', 'enter_tag']] = (1, 'buy_signal')

        return dataframe

    def custom_exit(self, pair: str, trade: Trade, current_time: datetime, current_rate: float,
                    current_profit: float, **kwargs):

        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        sl_tp_ratio = 2
        # sl_tp_ratio = self.sell_exit_ratio  # Hyperopt
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

        conditions = []

        conditions.append((dataframe['wma14']).shift(1) > dataframe['wma14'])

        if self.sell_wma_grow_older.value:
            conditions.append((dataframe['wma14']).shift(2) > dataframe['wma14'].shift(1))

        if self.sell_rsi_lookback_candles.value == 2:
            conditions.append(
                (qtpylib.crossed_below(dataframe['rsi'].shift(1), self.sell_rsi_value.value)) |
                (qtpylib.crossed_below(dataframe['rsi'].shift(2), self.sell_rsi_value.value))
            )
        if self.sell_rsi_lookback_candles.value == 3:
            conditions.append(
                (qtpylib.crossed_below(dataframe['rsi'].shift(1), self.sell_rsi_value.value)) |
                (qtpylib.crossed_below(dataframe['rsi'].shift(2), self.sell_rsi_value.value)) |
                (qtpylib.crossed_below(dataframe['rsi'].shift(3), self.sell_rsi_value.value))
            )
        if self.sell_rsi_lookback_candles.value == 4:
            conditions.append(
                (qtpylib.crossed_below(dataframe['rsi'].shift(1), self.sell_rsi_value.value)) |
                (qtpylib.crossed_below(dataframe['rsi'].shift(2), self.sell_rsi_value.value)) |
                (qtpylib.crossed_below(dataframe['rsi'].shift(3), self.sell_rsi_value.value)) |
                (qtpylib.crossed_below(dataframe['rsi'].shift(4), self.sell_rsi_value.value))
            )
        if self.sell_rsi_lookback_candles.value == 5:
            conditions.append(
                (qtpylib.crossed_below(dataframe['rsi'].shift(1), self.sell_rsi_value.value)) |
                (qtpylib.crossed_below(dataframe['rsi'].shift(2), self.sell_rsi_value.value)) |
                (qtpylib.crossed_below(dataframe['rsi'].shift(3), self.sell_rsi_value.value)) |
                (qtpylib.crossed_below(dataframe['rsi'].shift(4), self.sell_rsi_value.value)) |
                (qtpylib.crossed_below(dataframe['rsi'].shift(5), self.sell_rsi_value.value))
            )

        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                ['exit_long', 'exit_tag']] = (1, 'exit_signal')

        return dataframe

    def create_supports(self, df):
        # Hardcoded... Sorry.
        df['time'] = df['date'].dt.strftime('%H:%M')
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
