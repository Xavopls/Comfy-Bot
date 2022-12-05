import numpy as np  # noqa
import pandas as pd


def create_supports(df):
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


def percentage(num1, num2):
    if num1 == num2:
        return 0
    elif num1 < num2:
        num1, num2 = num2, num1
    return (num1 / num2 - 1) * 100


def reset_cumsum(df, series, reset_time):
    """
    Given a series and a df, it cumsums it and resets the sum at the given time.
    Returns a series.
    """
    df['tmp_data'] = series
    time = df['date'].dt.strftime('%H:%M')
    df['reset_time'] = np.where((time == reset_time), 1, 0)
    df['cumsum'] = df['reset_time'].cumsum()
    res = df.groupby(df['cumsum'])['tmp_data'].cumsum()
    return res


def custom_vwap(df, reset_time):
    df['time'] = df['date'].dt.strftime('%H:%M')
    df['reset_time'] = np.where((df['time'] == reset_time), 1, 0)

    typical = ((df['high'] + df['low'] + df['close']) / 3).values
    volume = df['volume'].values

    tpv = reset_cumsum(df=df, series=(typical * volume), reset_time=reset_time)
    cum_vol = reset_cumsum(df=df, series=volume, reset_time=reset_time)

    return pd.Series(index=df.index,
                     data=tpv / cum_vol)


def custom_session(df, start, end):
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