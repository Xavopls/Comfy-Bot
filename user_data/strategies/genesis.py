# ToDo:

# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
from functools import reduce
from json import load
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame

from freqtrade.strategy import (BooleanParameter, CategoricalParameter, DecimalParameter,
                                IStrategy, IntParameter, informative, merge_informative_pair)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


# This class is a sample. Feel free to customize it.
class Genesis(IStrategy):
    """
    This is a sample strategy to inspire you.
    More information in https://www.freqtrade.io/en/latest/strategy-customization/

    You can:
        :return: a Dataframe with all mandatory indicators for the strategies
    - Rename the class name (Do not forget to update class_name)
    - Add any methods you want to build your strategy
    - Add any lib you need to build your strategy

    You must keep:
    - the lib in the section "Do not remove these libs"
    - the methods: populate_indicators, populate_entry_trend, populate_exit_trend
    You should keep:
    - timeframe, minimal_roi, stoploss, trailing_*
    """
    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Can this strategy go short?
    can_short: bool = False

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        "0": 0.082,
        "4": 0.031,
        "14": 0.012,
        "38": 0
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.339

    # Trailing stoploss
    trailing_stop = True
    trailing_stop_positive = 0.231
    trailing_stop_positive_offset = 0.286
    trailing_only_offset_is_reached = False


    # Optimal timeframe for the strategy.
    timeframe = '1m'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    @informative('5m')
    def populate_indicators_5m(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_upperband'] = bollinger['upper']
        return dataframe

    @property
    def protections(self):
        prot = []
        ############ START HYPEROPT  ############
        # if self.use_stop_protection.value:
        #     prot.append({
        #         "method": "StoplossGuard",
        #         "lookback_period_candles": 24 * 3,
        #         "trade_limit": self.trade_limit.value,
        #         "stop_duration_candles": self.stop_duration.value,
        #         "only_per_pair": False
        #     })
        ############ END HYPEROPT  ############

        prot.append({
            "method": "StoplossGuard",
            "lookback_period_candles": 24 * 3,
            "trade_limit": 3,
            "stop_duration_candles": 10,
            "only_per_pair": False
        })

        return prot

    # Hyperoptable parameters

    # Protections
    use_stop_protection = BooleanParameter(default=True, space="protection", optimize=True)
    trade_limit = IntParameter(low=2, high=4, default=2, space='protection', optimize=True, load=True)
    stop_duration = IntParameter(low=10, high=60, default=10, space='protection', optimize=True, load=True)


    # Bollinger bands
    buy_bb_width_percentage = DecimalParameter(low=0.01, high=1, decimals=3, default=0.5, space='buy', optimize=True, load=True)
    sell_bb_width_percentage = DecimalParameter(low=0.01, high=1, decimals=3, default=0.5, space='sell', optimize=True, load=True)
    # buy_low_bb_enabled = BooleanParameter(default=True, space="buy")
    # buy_low_bb_error = IntParameter(low=-3, high=3, default=0, space='buy', optimize=True, load=True)
    sell_upper_bb_enabled = BooleanParameter(default=True, space="sell")
    sell_upper_bb_error = IntParameter(low=-3, high=3, default=0, space='sell', optimize=True, load=True)

    # Informative Pairs
    sell_informative_5m_bb_upperband = BooleanParameter(default=True, space='sell')

    # MFI
    buy_mfi_enabled = BooleanParameter(default=True, space='buy')
    sell_mfi_enabled = BooleanParameter(default=True, space='sell')
    buy_mfi = DecimalParameter(low=2, high=35, decimals=1, default=20, space='buy', optimize=True, load=True)
    sell_mfi = DecimalParameter(low=70, high=100, decimals=1, default=20, space='sell', optimize=True, load=True)

    # RSI
    buy_rsi_enabled = BooleanParameter(default=True, space='buy')
    buy_rsi = DecimalParameter(low=20, high=38, decimals=1, default=30, space='buy', optimize=True, load=True)

    sell_rsi_enabled = BooleanParameter(default=True, space='sell')
    sell_rsi = DecimalParameter(low=50, high=90, decimals=1, default=60, space='sell', optimize=True, load=True)

    # MACD
    buy_macd_enabled = BooleanParameter(default=True, space='buy')
    buy_macd = DecimalParameter(low=-10, high=10, decimals=2, default=-3, space='buy', optimize=True, load=True)
    sell_macd = DecimalParameter(low=0, high=15, decimals=2, default=-3, space='sell', optimize=True, load=True)

    # EMA
    buy_ema5_enabled = BooleanParameter(default=True, space='buy')

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

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
            'bb_upperband': {'color': 'blue'},
            'bb_lowerband': {'color': 'red'},
            # 'sma5': {'color': 'yellow'},
            # 'sma8': {'color': 'purple'},
            # 'sma13': {'color': 'blue'}
        },
        'subplots': {
            # "Hilberto": {
            #     'htleadsine': {'color': 'blue'},
            #     'htsine': {'color': 'red'}
            # },
            # "AROON": {
            #     'aroonosc': {'color': 'orange'}
            # },
            #
            "RSI": {
                'rsi': {'color': 'purple'},
                'rsi_sma': {'color': 'yellow'},
            },

            "MACD": {
                'macd': {'color': 'black'},
            },

            "MFI": {
                'mfi': {'color': 'black'},
            },
            "CCI": {
                'cci': {'color': 'brown'},
            },
            "Stoch_fast": {
                'fastd': {'color': 'blue'},
                'fastk': {'color': 'red'}
            },
            "Stoch_slow": {
                'slowd': {'color': 'blue'},
                'slowk': {'color': 'red'}
            },

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
        informative_pairs = [("ETH/USDT", "5m")]

        return informative_pairs

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

        # Momentum Indicators
        # ------------------------------------

        # ADX
        # dataframe['adx'] = ta.ADX(dataframe)

        # # Plus Directional Indicator / Movement
        # dataframe['plus_dm'] = ta.PLUS_DM(dataframe)
        # dataframe['plus_di'] = ta.PLUS_DI(dataframe)

        # # Minus Directional Indicator / Movement
        # dataframe['minus_dm'] = ta.MINUS_DM(dataframe)
        # dataframe['minus_di'] = ta.MINUS_DI(dataframe)

        # # Aroon, Aroon Oscillator
        # aroon = ta.AROON(dataframe)
        # dataframe['aroonup'] = aroon['aroonup']
        # dataframe['aroondown'] = aroon['aroondown']
        # dataframe['aroonosc'] = ta.AROONOSC(dataframe)

        # # Awesome Oscillator
        # dataframe['ao'] = qtpylib.awesome_oscillator(dataframe)

        # # Keltner Channel
        # keltner = qtpylib.keltner_channel(dataframe)
        # dataframe["kc_upperband"] = keltner["upper"]
        # dataframe["kc_lowerband"] = keltner["lower"]
        # dataframe["kc_middleband"] = keltner["mid"]
        # dataframe["kc_percent"] = (
        #     (dataframe["close"] - dataframe["kc_lowerband"]) /
        #     (dataframe["kc_upperband"] - dataframe["kc_lowerband"])
        # )
        # dataframe["kc_width"] = (
        #     (dataframe["kc_upperband"] - dataframe["kc_lowerband"]) / dataframe["kc_middleband"]
        # )

        # # Ultimate Oscillator
        # dataframe['uo'] = ta.ULTOSC(dataframe)

        # Commodity Channel Index: values [Oversold:-100, Overbought:100]
        dataframe['cci'] = ta.CCI(dataframe)

        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        dataframe['rsi_sma'] = ta.SMA(dataframe['rsi'])
        # # Inverse Fisher transform on RSI: values [-1.0, 1.0] (https://goo.gl/2JGGoy)
        # rsi = 0.1 * (dataframe['rsi'] - 50)
        # dataframe['fisher_rsi'] = (np.exp(2 * rsi) - 1) / (np.exp(2 * rsi) + 1)

        # # Inverse Fisher transform on RSI normalized: values [0.0, 100.0] (https://goo.gl/2JGGoy)
        # dataframe['fisher_rsi_norma'] = 50 * (dataframe['fisher_rsi'] + 1)

        # # Stochastic Slow
        stoch = ta.STOCH(dataframe)
        dataframe['slowd'] = stoch['slowd']
        dataframe['slowk'] = stoch['slowk']

        # Stochastic Fast
        stoch_fast = ta.STOCHF(dataframe)
        dataframe['fastd'] = stoch_fast['fastd']
        dataframe['fastk'] = stoch_fast['fastk']

        # # Stochastic RSI
        # Please read https://github.com/freqtrade/freqtrade/issues/2961 before using this.
        # STOCHRSI is NOT aligned with tradingview, which may result in non-expected results.
        # stoch_rsi = ta.STOCHRSI(dataframe)
        # dataframe['fastd_rsi'] = stoch_rsi['fastd']
        # dataframe['fastk_rsi'] = stoch_rsi['fastk']

        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']

        # MFI
        dataframe['mfi'] = ta.MFI(dataframe)

        # # ROC
        # dataframe['roc'] = ta.ROC(dataframe)

        # Overlap Studies
        # ------------------------------------

        # Bollinger Bands
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_lowerband'] = bollinger['lower']
        dataframe['bb_middleband'] = bollinger['mid']
        dataframe['bb_upperband'] = bollinger['upper']
        dataframe['bb_width_percentage'] = ((dataframe['bb_lowerband'] / dataframe['bb_upperband']) - 1) * -100

        # Bollinger Bands - Weighted (EMA based instead of SMA)
        # weighted_bollinger = qtpylib.weighted_bollinger_bands(
        #     qtpylib.typical_price(dataframe), window=20, stds=2
        # )
        # dataframe["wbb_upperband"] = weighted_bollinger["upper"]
        # dataframe["wbb_lowerband"] = weighted_bollinger["lower"]
        # dataframe["wbb_middleband"] = weighted_bollinger["mid"]
        # dataframe["wbb_percent"] = (
        #     (dataframe["close"] - dataframe["wbb_lowerband"]) /
        #     (dataframe["wbb_upperband"] - dataframe["wbb_lowerband"])
        # )
        # dataframe["wbb_width"] = (
        #     (dataframe["wbb_upperband"] - dataframe["wbb_lowerband"]) /
        #     dataframe["wbb_middleband"]
        # )

        # # EMA - Exponential Moving Average
        # dataframe['ema3'] = ta.EMA(dataframe, timeperiod=3)
        # dataframe['ema5'] = ta.EMA(dataframe, timeperiod=5)
        # dataframe['ema10'] = ta.EMA(dataframe, timeperiod=10)
        # dataframe['ema10'] = ta.EMA(dataframe, timeperiod=10)
        # dataframe['ema21'] = ta.EMA(dataframe, timeperiod=21)
        # dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        # dataframe['ema100'] = ta.EMA(dataframe, timeperiod=100)

        # # SMA - Simple Moving Average
        # dataframe['sma3'] = ta.SMA(dataframe, timeperiod=3)
        # dataframe['sma13'] = ta.SMA(dataframe, timeperiod=13)
        # dataframe['sma5'] = ta.SMA(dataframe, timeperiod=5)
        # dataframe['sma8'] = ta.SMA(dataframe, timeperiod=8)
        # dataframe['sma21'] = ta.SMA(dataframe, timeperiod=21)
        # dataframe['sma50'] = ta.SMA(dataframe, timeperiod=50)
        # dataframe['sma100'] = ta.SMA(dataframe, timeperiod=100)

        # Parabolic SAR
        # dataframe['sar'] = ta.SAR(dataframe)

        # TEMA - Triple Exponential Moving Average
        dataframe['tema'] = ta.TEMA(dataframe, timeperiod=9)

        # Cycle Indicator
        # ------------------------------------
        # Hilbert Transform Indicator - SineWave
        hilbert = ta.HT_SINE(dataframe)
        dataframe['htsine'] = hilbert['sine']
        dataframe['htleadsine'] = hilbert['leadsine']

        # Pattern Recognition - Bullish candlestick patterns
        # ------------------------------------
        # # Hammer: values [0, 100]
        # dataframe['CDLHAMMER'] = ta.CDLHAMMER(dataframe)
        # # Inverted Hammer: values [0, 100]
        # dataframe['CDLINVERTEDHAMMER'] = ta.CDLINVERTEDHAMMER(dataframe)
        # # Dragonfly Doji: values [0, 100]
        # dataframe['CDLDRAGONFLYDOJI'] = ta.CDLDRAGONFLYDOJI(dataframe)
        # # Piercing Line: values [0, 100]
        # dataframe['CDLPIERCING'] = ta.CDLPIERCING(dataframe) # values [0, 100]
        # # Morningstar: values [0, 100]
        # dataframe['CDLMORNINGSTAR'] = ta.CDLMORNINGSTAR(dataframe) # values [0, 100]
        # # Three White Soldiers: values [0, 100]
        # dataframe['CDL3WHITESOLDIERS'] = ta.CDL3WHITESOLDIERS(dataframe) # values [0, 100]

        # Pattern Recognition - Bearish candlestick patterns
        # ------------------------------------
        # # Hanging Man: values [0, 100]
        # dataframe['CDLHANGINGMAN'] = ta.CDLHANGINGMAN(dataframe)
        # # Shooting Star: values [0, 100]
        # dataframe['CDLSHOOTINGSTAR'] = ta.CDLSHOOTINGSTAR(dataframe)
        # # Gravestone Doji: values [0, 100]
        # dataframe['CDLGRAVESTONEDOJI'] = ta.CDLGRAVESTONEDOJI(dataframe)
        # # Dark Cloud Cover: values [0, 100]
        # dataframe['CDLDARKCLOUDCOVER'] = ta.CDLDARKCLOUDCOVER(dataframe)
        # # Evening Doji Star: values [0, 100]
        # dataframe['CDLEVENINGDOJISTAR'] = ta.CDLEVENINGDOJISTAR(dataframe)
        # # Evening Star: values [0, 100]
        # dataframe['CDLEVENINGSTAR'] = ta.CDLEVENINGSTAR(dataframe)

        # Pattern Recognition - Bullish/Bearish candlestick patterns
        # ------------------------------------
        # # Three Line Strike: values [0, -100, 100]
        # dataframe['CDL3LINESTRIKE'] = ta.CDL3LINESTRIKE(dataframe)
        # # Spinning Top: values [0, -100, 100]
        # dataframe['CDLSPINNINGTOP'] = ta.CDLSPINNINGTOP(dataframe) # values [0, -100, 100]
        # # Engulfing: values [0, -100, 100]
        # dataframe['CDLENGULFING'] = ta.CDLENGULFING(dataframe) # values [0, -100, 100]
        # # Harami: values [0, -100, 100]
        # dataframe['CDLHARAMI'] = ta.CDLHARAMI(dataframe) # values [0, -100, 100]
        # # Three Outside Up/Down: values [0, -100, 100]
        # dataframe['CDL3OUTSIDE'] = ta.CDL3OUTSIDE(dataframe) # values [0, -100, 100]
        # # Three Inside Up/Down: values [0, -100, 100]
        # dataframe['CDL3INSIDE'] = ta.CDL3INSIDE(dataframe) # values [0, -100, 100]

        # # Chart type
        # # ------------------------------------
        # # Heikin Ashi Strategy
        # heikinashi = qtpylib.heikinashi(dataframe)
        # dataframe['ha_open'] = heikinashi['open']
        # dataframe['ha_close'] = heikinashi['close']
        # dataframe['ha_high'] = heikinashi['high']
        # dataframe['ha_low'] = heikinashi['low']

        # Retrieve best bid and best ask from the orderbook
        # ------------------------------------
        """
        # first check if dataprovider is available
        if self.dp:
            if self.dp.runmode.value in ('live', 'dry_run'):
                ob = self.dp.orderbook(metadata['pair'], 1)
                dataframe['best_bid'] = ob['bids'][0][0]
                dataframe['best_ask'] = ob['asks'][0][0]
        """

        # Custom

        # Bullish Inverted hammer
        # - Bullish
        # - Head bigger than body
        # - Super tiny tail < 3.5$
        dataframe['candle_bullish_inverted_hammer'] = \
            (dataframe['open'] < dataframe['close']) & \
            ((dataframe['close'] - dataframe['open']) < (dataframe['high'] - dataframe['close'])) & \
            ((dataframe['open'] - dataframe['low']) < 3.5)

        # Hammer Bearish
        # - Head inexistant
        # - Tail > Body
        # - Body > 0.3%
        # - Open > Close
        dataframe['candle_hammer_bearish'] = \
            (dataframe['high'] - dataframe['open'] < 1) & \
            (dataframe['close'] < dataframe['open']) & \
            ((1 - (dataframe['close'] / dataframe['open'])) > 0.003) & \
            ((dataframe['open'] - dataframe['close']) < (dataframe['close'] - dataframe['low']))

        # Bullish 3% candle
        # - Bullish
        # - 3% open-close
        dataframe['candle_bullish_3%'] = \
            (dataframe['open'] < dataframe['close']) & \
            (dataframe['close'] * 100 / dataframe['open'] > 103)

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with entry columns populated
        """
        ########################### START HYPEROPT ###########################
        # conditions = []
        #
        # # Bollinger bands
        # conditions.append((dataframe['bb_width_percentage']) > self.buy_bb_width_percentage.value)
        # conditions.append((dataframe['bb_lowerband'] > dataframe['low']))
        #
        # # RSI
        # conditions.append(dataframe['rsi'] < self.buy_rsi.value)
        #
        # # MACD
        # conditions.append(dataframe['macd'] < self.buy_macd.value)
        #
        # # MFI
        # if self.buy_mfi_enabled:
        #     conditions.append(dataframe['mfi'] < self.buy_mfi.value)
        #
        # # Other
        # conditions.append((dataframe['volume'] > 0))
        #
        # if conditions:
        #     dataframe.loc[
        #         reduce(lambda x, y: x & y, conditions),
        #         'enter_long'] = 1
        ########################### END HYPEROPT ###########################

        dataframe.loc[
            (
                (dataframe['bb_width_percentage'] > 0.629) &
                (dataframe['bb_lowerband'] > dataframe['low']) &
                (dataframe['rsi'] < 30.3) &
                (dataframe['macd'] < 8.76) &
                (dataframe['mfi'] < 2.1) &

                # Volume not 0
                (dataframe['volume'] > 0)
            ),
            ['enter_long', 'enter_tag']] = (1, 'minor_low')

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the exit signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with exit columns populated
        """

        ########################### START HYPEROPT ###########################

        # conditions = []
        #
        # # Bollingers
        # conditions.append((dataframe['high'] > dataframe['bb_upperband']))
        # conditions.append((dataframe['high_5m'] > dataframe['bb_upperband_5m']))
        # conditions.append((dataframe['bb_width_percentage']) > self.sell_bb_width_percentage.value)
        #
        # # RSI
        # conditions.append(dataframe['rsi'] > self.sell_rsi.value)
        #
        # # MACD
        # conditions.append(dataframe['macd'] > self.sell_macd.value)
        #
        # # MFI
        # if self.sell_mfi_enabled:
        #     conditions.append(dataframe['mfi'] > self.sell_mfi.value)
        #
        # if conditions:
        #     dataframe.loc[
        #         reduce(lambda x, y: x & y, conditions),
        #         'exit_long'] = 1

        ########################### END HYPEROPT ###########################

        dataframe.loc[
            (
                (dataframe['rsi'] > 81.9) &
                (dataframe['mfi'] > 79.7) &
                (dataframe['macd'] > 14.33) &

                (dataframe['high'] > dataframe['bb_upperband']) &
                (dataframe['high_5m'] > dataframe['bb_upperband_5m']) &
                (dataframe['bb_width_percentage'] > 0.506) &

                (dataframe['volume'] > 0)  # Make sure Volume is not 0
            ),

            ['exit_long', 'exit_tag']] = (1, 'exit_1')

        return dataframe

    # Support methods

    # 1m methods
    def entry_strat_1(self, dataframe: DataFrame):
        return (
                (dataframe['rsi'] - dataframe['rsi'].shift(1) > 7.5) &
                (dataframe['rsi'] < 42) &
                (qtpylib.crossed_above(dataframe['rsi'], dataframe['rsi_sma']))
        )

    def entry_strat_max_mins(self, dataframe: DataFrame):
        return (
            (dataframe['low'] > dataframe['low'].shift(30).rolling(300).max().shift())
        )

    def exit_strat_1(self, dataframe: DataFrame):
        return (
            (qtpylib.crossed_above(dataframe['macd'], 0))
        )

    # 5m methods
    def entry_test_bbs(self, dataframe: DataFrame):
        return (

            # Bullish candle
            # (dataframe['open'] < dataframe['close']) &

            # last candle low below lower BB
            # (dataframe['low'].shift(1) < dataframe['bb_lowerband']) &

            ## Last candle bearish
            # (dataframe['open'].shift(1) > dataframe['close'].shift(1)) &

            ## MACD above -4
            # (dataframe['macd'] > -4)

            # rsi = 30
                dataframe['rsi'] > 30
        )

    def exit_test(self, dataframe: DataFrame):
        return (

            # Bearish candle
            # (dataframe['open'] > dataframe['close']) &

            # Last candle bullish
            # (dataframe['open'].shift(1) < dataframe['close'].shift(1)) &

            # Candle above BB upperband
            # (dataframe['high'] > dataframe['bb_upperband'])

        )

    # 30m methods
    def huge_peak_bullish(self, dataframe: DataFrame):
        return (
            # Aroon osc on previous candle is -100
                (dataframe['aroonosc'].shift(1) < -70) &

                # Bullish candle
                (dataframe['open'] < dataframe['close']) &

                # Candle with high above lower BB
                (dataframe['high'] > dataframe['bb_lowerband']) &

                # Prior 4 candles bearish
                (dataframe['open'].shift(1) > dataframe['close'].shift(1)) &
                (dataframe['open'].shift(2) > dataframe['close'].shift(2)) &
                (dataframe['open'].shift(3) > dataframe['close'].shift(3)) &
                (dataframe['open'].shift(4) > dataframe['close'].shift(4)) &

                # Prior 4 candles lows below BB
                (dataframe['low'].shift(1) < dataframe['bb_lowerband'].shift(1)) &
                (dataframe['low'].shift(2) < dataframe['bb_lowerband'].shift(2)) &
                (dataframe['low'].shift(3) < dataframe['bb_lowerband'].shift(3)) &
                (dataframe['low'].shift(4) < dataframe['bb_lowerband'].shift(4)) &

                # RSI below 30
                (dataframe['rsi'] < 30) &

                # Downhill heavier than 3.5%
                (((1 - dataframe['low'].shift(1) / dataframe['high'].shift(4)) * 100) > 3.5)
        )
