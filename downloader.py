import ccxt
from ccxt.base.errors import RequestTimeout
import pandas as pd
from datetime import datetime
from datetime import timedelta
import time


binance = ccxt.binance()


def to_timestamp(dt):
    return binance.parse8601(dt.isoformat())


def download(symbol, start, end):
    '''
    Download all the transaction for a given symbol from the start date to the end date
    @param symbol: the symbol of the coin for which download the transactions
    @param start: the start date from which download the transaction
    @param end: the end date from which download the transaction
    '''

    records = []
    since = start
    ten_minutes = 60000 * 10

    print('Downloading {} from {} to {}'.format(symbol, binance.iso8601(start), binance.iso8601(end)))

    while since < end:
        #print('since: ' + binance.iso8601(since)) #uncomment this line of code for verbose download
        try:
            orders = binance.fetch_trades(symbol + '/BTC', since)
        except RequestTimeout:
            time.sleep(5)
            orders = binance.fetch_trades(symbol + '/BTC', since)

        if len(orders) > 0:

            latest_ts = orders[-1]['timestamp']
            if since != latest_ts:
                since = latest_ts
            else:
                since += ten_minutes

            for l in orders:
                records.append({
                    'symbol': l['symbol'],
                    'timestamp': l['timestamp'],
                    'datetime': l['datetime'],
                    'side': l['side'],
                    'price': l['price'],
                    'amount': l['amount'],
                    'btc_volume': float(l['price']) * float(l['amount']),
                })
        else:
            since += ten_minutes

    return pd.DataFrame.from_records(records)


def download_binance(days_before=7, days_after=7, skip_bad=False):
    '''
    Download all the transactions for all the pumps in binance in a given interval
    @param days_before: the number of days before the pump
    @param days_after: the number of days after the pump
    @param skip_bad: set this parameter to True if you do not want to download the pumps annotated as 'bad_pump'
    '''

    df = pd.read_csv('pump_telegram.csv')
    binance_only = df[df['exchange'] == 'binance']

    for i, pump in binance_only.iterrows():
        symbol = pump['symbol']
        date = pump['date'] + ' ' + pump['hour']
        if skip_bad and pump['notes'] == 'bad_pump':
            continue
        pump_time = datetime.strptime(date, "%Y-%m-%d %H:%M")
        before = to_timestamp(pump_time - timedelta(days=days_before))
        after = to_timestamp(pump_time + timedelta(days=days_after))
        df = download(symbol, before, after)
        df.to_csv('data/{}_{}'.format(symbol, str(date).replace(':', '.') + '.csv'), index=False)


if __name__ == '__main__':
    download_binance(days_before=7, days_after=7)
