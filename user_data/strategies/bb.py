# ToDo:
# Trailing stop, check: ( last candle volume, candle type, candle volatility)
# Check: Elder's triple screen trading system
# Gather data from sp500 on freqtrade's https://www.freqtrade.io/en/stable/strategy-callbacks/#bot-loop-start


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
import utils.strategy_utils as utils
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

    # Trailing stoploss
    trailing_stop = True,
    trailing_stop_positive = 0.086,
    trailing_stop_positive_offset = 0.141,
    trailing_only_offset_is_reached = True

    # Optimal timeframe for the strategy.
    timeframe = '5m'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Hyperoptable parameters
    # buy_us_market_hours = BooleanParameter(default=False, space="buy", optimize=True)
    # buy_only_weekdays = BooleanParameter(default=False, space="buy", optimize=True)
    # buy_vwap_option = CategoricalParameter(["above", "below", "no"], default="no", space="buy")
    #
    # sell_support_margin_percentage = DecimalParameter(low=0.99, high=1.00, decimals=3,
    #                                                   default=1.0, space='sell', optimize=True)
    # sell_partial_exit_ratio = DecimalParameter(low=0.5, high=1.5, decimals=1,
    #                                            default=1.5, space='sell', optimize=True)
    # sell_exit_ratio = DecimalParameter(low=1.6, high=3, decimals=1,
    #                                    default=2, space='sell', optimize=True)
    #
    # cooldown_lookback = IntParameter(24, 60, default=5, space="protection", optimize=True)
    # sl_guard_trade_limit = IntParameter(1, 5, default=2, space="protection", optimize=True)
    # sl_guard_lookback_hours = IntParameter(1, 8, default=2, space="protection", optimize=True)
    # sl_guard_stop_duration = IntParameter(12, 200, default=5, space="protection", optimize=True)
    # sl_guard_use = BooleanParameter(default=True, space="protection", optimize=True)

    buy_us_market_hours = True
    buy_only_weekdays = True
    buy_vwap_option = 'below'
    sell_support_margin_percentage = 0.992
    sell_partial_exit_ratio = 1
    sell_exit_ratio = 3
    cooldown_lookback = 41
    sl_guard_trade_limit = 1
    sl_guard_lookback_hours = 1
    sl_guard_stop_duration = 153
    sl_guard_use = True

    @property
    def protections(self):
        prot = []

        prot.append({
            "method": "CooldownPeriod",
            "stop_duration_candles": self.cooldown_lookback
        })
        if self.sl_guard_use:
            prot.append({
                "method": "StoplossGuard",
                "lookback_period_candles": 12 * self.sl_guard_lookback_hours,
                "trade_limit": self.sl_guard_trade_limit,
                "stop_duration_candles": self.sl_guard_stop_duration,
                "only_per_pair": False
            })
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

        # return informative_pairs

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

        dataframe['vwap'] = utils.custom_vwap(dataframe, '01:00')
        dataframe = utils.create_supports(dataframe)
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
        dataframe['zero'] = 0
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
            stoploss_price = trade_candle['support'] * self.sell_support_margin_percentage  # Hyperopt
            # stoploss_price = trade_candle['support']
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
        # resize_position_ratio = 1.5
        resize_position_ratio = self.sell_partial_exit_ratio  # Hyperopt
        # Price to resize
        resize_position_rate = (trade.open_rate + resize_position_ratio * (trade.open_rate - trade.stop_loss))

        if current_rate >= resize_position_rate and trade.nr_of_successful_exits == 0:
            # Take half of the profit at 1:1.5
            return -(trade.stake_amount / 2)

        return None

    def custom_stake_amount(self, pair: str, current_time: datetime, current_rate: float,
                            proposed_stake: float, min_stake: Optional[float], max_stake: float,
                            leverage: float, entry_tag: Optional[str], side: str,
                            **kwargs) -> float:

        dataframe, _ = self.dp.get_analyzed_dataframe(pair=pair, timeframe=self.timeframe)
        current_candle = dataframe.iloc[-1].squeeze()

        sl_percentage = (current_rate / current_candle['support'] - 1) * 100

        # Case where SL < 1%. We can't leverage, so we can't reach 1% atm.
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

        conditions.append(dataframe['wt1'] < 0)
        conditions.append(dataframe['wt2'] < 0)
        conditions.append(qtpylib.crossed_above(dataframe['close'], dataframe['ema12']))
        conditions.append((dataframe['volume'] > 0))

        # Volume not 0
        conditions.append(dataframe['volume'] > 0)

        if self.buy_vwap_option == 'above':
            conditions.append(dataframe['hlc3'] > dataframe['vwap'])

        if self.buy_vwap_option == 'below':
            conditions.append(dataframe['hlc3'] < dataframe['vwap'])

        if self.buy_us_market_hours:
            conditions.append(dataframe['time'] >= '13:30')
            conditions.append(dataframe['time'] <= '20:00')

        if self.buy_only_weekdays:
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
        # sl_tp_ratio = 2
        sl_tp_ratio = self.sell_exit_ratio  # Hyperopt
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
