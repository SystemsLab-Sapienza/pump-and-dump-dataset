import glob
import datetime
import os
import numpy as np
import pandas as pd

path = 'data/*.csv'

def std_rush_order_feature(df_buy, time_freq, rolling_freq):
    df_buy = df_buy.groupby(df_buy.index).count()
    df_buy[df_buy == 1] = 0
    df_buy[df_buy > 1] = 1
    buy_volume = df_buy.groupby(pd.Grouper(freq=time_freq))['btc_volume'].sum()
    buy_count = df_buy.groupby(pd.Grouper(freq=time_freq))['btc_volume'].count()
    buy_volume.drop(buy_volume[buy_count == 0].index, inplace=True)
    buy_volume.dropna(inplace=True)
    rolling_diff = buy_volume.rolling(window=rolling_freq).std()
    results = rolling_diff.pct_change()
    return results


def avg_rush_order_feature(df_buy, time_freq, rolling_freq):
    df_buy = df_buy.groupby(df_buy.index).count()
    df_buy[df_buy == 1] = 0
    df_buy[df_buy > 1] = 1
    buy_volume = df_buy.groupby(pd.Grouper(freq=time_freq))['btc_volume'].sum()
    buy_count = df_buy.groupby(pd.Grouper(freq=time_freq))['btc_volume'].count()
    buy_volume.drop(buy_volume[buy_count == 0].index, inplace=True)
    buy_volume.dropna(inplace=True)
    rolling_diff = buy_volume.rolling(window=rolling_freq).mean()
    results = rolling_diff.pct_change()
    return results


def std_trades_feature(df_buy_rolling, rolling_freq):
    buy_volume = df_buy_rolling['price'].count()
    buy_volume.drop(buy_volume[buy_volume == 0].index, inplace=True)
    buy_volume.dropna(inplace=True)
    rolling_diff = buy_volume.rolling(window=rolling_freq).std()
    results = rolling_diff.pct_change()
    return results


def std_volume_feature(df_buy_rolling, rolling_freq):
    buy_volume = df_buy_rolling['btc_volume'].sum()
    buy_volume.drop(buy_volume[buy_volume == 0].index, inplace=True)
    buy_volume.dropna(inplace=True)
    rolling_diff = buy_volume.rolling(window=rolling_freq).std()
    results = rolling_diff.pct_change()
    return results


def avg_volume_feature(df_buy_rolling, rolling_freq):
    buy_volume = df_buy_rolling['btc_volume'].sum()
    buy_volume.drop(buy_volume[buy_volume == 0].index, inplace=True)
    buy_volume.dropna(inplace=True)
    rolling_diff = buy_volume.rolling(window=rolling_freq).mean()
    results = rolling_diff.pct_change()
    return results


def std_price_feature(df_buy_rolling, rolling_freq):
    buy_volume = df_buy_rolling['price'].mean()
    buy_volume.dropna(inplace=True)
    rolling_diff = buy_volume.rolling(window=rolling_freq).std()
    results = rolling_diff.pct_change()
    return results


def avg_price_feature(df_buy_rolling):
    buy_volume = df_buy_rolling['price'].mean()
    buy_volume.dropna(inplace=True)
    rolling_diff = buy_volume.rolling(window=10).mean()
    results = rolling_diff.pct_change()
    return results


def avg_price_max(df_buy_rolling):
    buy_volume = df_buy_rolling['price'].max()
    buy_volume.dropna(inplace=True)
    rolling_diff = buy_volume.rolling(window=10).mean()
    results = rolling_diff.pct_change()
    return results


def chunks_time(df_buy_rolling):
    # compute any kind of aggregation
    buy_volume = df_buy_rolling['price'].max()
    buy_volume.dropna(inplace=True)
    #the index contains time info
    return buy_volume.index


def build_features(file, coin, time_freq, rolling_freq, index):
    df = pd.read_csv(file)
    df["time"] = pd.to_datetime(df['timestamp'].astype(np.int64), unit='ms')
    df = df.reset_index().set_index('time')

    df_buy = df[df['side'] == 'buy']

    df_buy_grouped = df_buy.groupby(pd.Grouper(freq=time_freq))

    date = chunks_time(df_buy_grouped)

    results_df = pd.DataFrame(
        {'date': date,
         'pump_index': index,
         'std_rush_order': std_rush_order_feature(df_buy, time_freq, rolling_freq).values,
         'avg_rush_order': avg_rush_order_feature(df_buy, time_freq, rolling_freq).values,
         'std_trades': std_trades_feature(df_buy_grouped, rolling_freq).values,
         'std_volume': std_volume_feature(df_buy_grouped, rolling_freq).values,
         'avg_volume': avg_volume_feature(df_buy_grouped, rolling_freq).values,
         'std_price': std_price_feature(df_buy_grouped, rolling_freq).values,
         'avg_price': avg_price_feature(df_buy_grouped),
         'avg_price_max': avg_price_max(df_buy_grouped).values,
         'hour_sin': np.sin(2 * np.pi * date.hour/23),
         'hour_cos': np.cos(2 * np.pi * date.hour/23),
         'minute_sin': np.sin(2 * np.pi * date.minute / 59),
         'minute_cos': np.cos(2 * np.pi * date.minute / 59),
         })

    results_df['symbol'] = coin
    results_df['gt'] = 0
    return results_df.dropna()


def build_features_multi(time_freq, rolling_freq):

    files = glob.glob(path)

    all_results_df = pd.DataFrame()
    count = 0
    pumps = pd.read_csv('pump_telegram.csv')
    pumps = pumps[pumps['exchange'] == 'binance']

    for f in files:
        print(f)
        coin_date, time = os.path.basename(f[:f.rfind('.')]).split(' ')
        coin, date = coin_date.split('_')

        skip_pump = len(pumps[(pumps['symbol'] == coin) & (pumps['date'] == date) & (pumps['hour'] == time.replace('.', ':'))]) == 0
        if skip_pump:
            continue

        results_df = build_features(f, coin, time_freq, rolling_freq, count)

        date_datetime = datetime.datetime.strptime(date + ' ' + time, '%Y-%m-%d %H.%M')

        # We consider 24 hours before and 24 hours after the pump
        results_df = results_df[(results_df['date'] >= date_datetime - datetime.timedelta(hours=24)) & (results_df['date'] <= date_datetime + datetime.timedelta(hours=24))]

        all_results_df = pd.concat([all_results_df, results_df])
        count += 1

    all_results_df.to_csv('features/features_{}.csv'.format(time_freq), index=False, float_format='%.3f')


def compute_features():
    build_features_multi(time_freq='25S', rolling_freq=900)
    build_features_multi(time_freq='15S', rolling_freq=900)
    build_features_multi(time_freq='5S', rolling_freq=700)


if __name__ == '__main__':
    start = datetime.datetime.now()
    compute_features()
    print(datetime.datetime.now() - start)
