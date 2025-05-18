# -*- coding: utf-8 -*-
"""
Created on Thu May  8 16:35:24 2025
market liquidity calculation

bid-offer spread
depths

15-min interval
@author: ruchuan2
"""

import pandas as pd
import numpy
import os

weather_data = pd.read_pickle(
    "/projects/illinois/aces/shared/ruchuan2/SP500/weather_data.pkl")

# checking some outliar
weather_data.loc[weather_data['precipitation'] < 0, 'precipitation'] = 0

weather_data = weather_data.groupby('timestamp', as_index=False)
weather_data_avg = weather_data['precipitation'].mean()

futures_quotes = sorted(os.listdir(
    "/projects/illinois/aces/shared/ruchuan2/SP500/front_month_book_cleaned/"))

futures_trades = sorted(os.listdir(
    "/projects/illinois/aces/shared/ruchuan2/SP500/front_month_trades_cleaned/"))


def futures_cal(quotes, trades):

    # delete observations with cross spreads and locked spreads

    quotes.drop(quotes[(quotes['Bid_PX_1'] == 0) | (quotes['Ask_PX_1'] == 0)].index,
                inplace=True)

    quotes.drop(quotes[quotes['Bid_PX_1'] >= quotes['Ask_PX_1']].index,
                inplace=True)

    quotes['time_diff'] = quotes['Time'].shift(
        -1) - quotes['Time']
    quotes['time_diff'] = quotes['time_diff'].dt.total_seconds()

    quotes.fillna(0, inplace=True)

    # basis points-- scaled to midpoint price
    quotes['midpoint'] = (quotes['Ask_PX_1']+quotes['Bid_PX_1'])/2
    quotes['spread'] = ((quotes['Ask_PX_1']-quotes['Bid_PX_1']) /
                        ((quotes['Ask_PX_1']+quotes['Bid_PX_1'])/2))*10000 * quotes['time_diff']

    # BBO dollar depth

    quotes['BBO'] = (quotes['Ask_PX_1']*quotes['Ask_Qty_1'] +
                     quotes['Bid_PX_1']*quotes['Bid_Qty_1'])*50/10**6 * quotes['time_diff']

    Non_BBO_ask = [f'Ask_PX_{i}' for i in range(1, 11)]
    Non_BBO_bid = [f'Bid_PX_{i}' for i in range(1, 11)]

    Non_BBO_ask_qty = [f'Ask_Qty_{i}' for i in range(1, 11)]
    Non_BBO_bid_qty = [f'Bid_Qty_{i}' for i in range(1, 11)]

    quotes['Non_BBO'] = (sum(quotes[px] * quotes[qty] for px, qty in zip(Non_BBO_ask, Non_BBO_ask_qty)) +
                         sum(quotes[px] * quotes[qty] for px, qty in zip(Non_BBO_bid, Non_BBO_bid_qty))*50)/10**6 * quotes['time_diff']

    quotes.set_index('Time', inplace=True)
    resample_15m_quotes = quotes.resample('15min').agg({
        'spread': 'sum',
        'time_diff': 'sum',
        'BBO': 'sum',
        'Non_BBO': 'sum'
    })

    # Calculate time-weighted average
    resample_15m_quotes['spread'] = resample_15m_quotes['spread'] / \
        resample_15m_quotes['time_diff']
    resample_15m_quotes['BBO'] = resample_15m_quotes['BBO'] / \
        resample_15m_quotes['time_diff']
    resample_15m_quotes['Non_BBO'] = resample_15m_quotes['Non_BBO'] / \
        resample_15m_quotes['time_diff']
    resample_15m_quotes['volatility'] = quotes['midpoint'].resample(
        '15min').std()
    del resample_15m_quotes['time_diff']

    trades.set_index('Time', inplace=True)

    # calculating the  dollar trading volume and number of trades
    trades['vol'] = trades['Size'] * trades['PX'] * 50/10**6

    resample_15m_trades = trades.resample('15min').agg({
        'vol': 'sum'})
    resample_15m_trades['#trades'] = trades.resample('15min').size()

    futures_data = pd.merge(resample_15m_quotes, resample_15m_trades, how='inner', left_index=True,
                            right_index=True)

    return futures_data


futures = list(map(lambda i: futures_cal(pd.read_pickle(f'/projects/illinois/aces/shared/ruchuan2/SP500/front_month_book_cleaned/{futures_quotes[i]}', compression='gzip'),
                                         pd.read_pickle(f'/projects/illinois/aces/shared/ruchuan2/SP500/front_month_trades_cleaned/{futures_trades[i]}', compression='gzip')),
                   range(len(futures_quotes))))

futures = pd.concat(futures)
print('futures finished')

etf_quotes = sorted(os.listdir(
    "/projects/illinois/aces/shared/ruchuan2/SP500/spy_nbbo/"))

etf_trades = sorted(os.listdir(
    "/projects/illinois/aces/shared/ruchuan2/SP500/spy_trades/"))


def etf_cal(quotes, trades):

    quotes['Time'] = pd.to_timedelta(
        quotes['time_m'], unit='s') + pd.to_datetime(quotes['date'])
    quotes['Time'] = pd.to_datetime(quotes['Time'])
    quotes['Time'] = quotes['Time'].dt.tz_localize('America/New_York')

    trades['Time'] = pd.to_timedelta(
        trades['time_m'], unit='s') + pd.to_datetime(trades['date'])
    trades['Time'] = pd.to_datetime(trades['Time'])
    trades['Time'] = trades['Time'].dt.tz_localize('America/New_York')

    # delete zero quote prices and observations with cross-spread and locked-spread

    quotes.drop(quotes[(quotes['bid'] == 0) | (
        quotes['ask'] == 0)].index, inplace=True)
    quotes.drop(quotes[quotes['bid'] >= quotes['ask']].index,
                inplace=True)

    quotes['time_diff'] = quotes['Time'].shift(
        -1) - quotes['Time']
    quotes['time_diff'] = quotes['time_diff'].dt.total_seconds()

    quotes.fillna(0, inplace=True)

    # midpoint price

    quotes['midpoint'] = (quotes['ask']+quotes['bid'])/2

    # basis points-- scaled to midpoint price
    quotes['spread'] = ((quotes['ask']-quotes['bid']) /
                        ((quotes['ask']+quotes['bid'])/2))*10000 * quotes['time_diff']

    # volatility

    # BBO dollar depth

    quotes['BBO'] = (quotes['ask']*quotes['asksiz'] +
                     quotes['bid']*quotes['bidsiz'])/10**6 * quotes['time_diff']

    quotes.set_index('Time', inplace=True)
    resample_15m_quotes = quotes.resample('15min').agg({
        'spread': 'sum',
        'time_diff': 'sum',
        'BBO': 'sum'
    })

    # Calculate time-weighted average
    resample_15m_quotes['spread'] = resample_15m_quotes['spread'] / \
        resample_15m_quotes['time_diff']
    resample_15m_quotes['BBO'] = resample_15m_quotes['BBO'] / \
        resample_15m_quotes['time_diff']
    resample_15m_quotes['volatility'] = quotes['midpoint'].resample(
        '15min').std()
    del resample_15m_quotes['time_diff']

    trades.set_index('Time', inplace=True)

    # calculating the  dollar trading volume and number of trades
    trades['vol'] = trades['size'] * trades['price']/10**6

    resample_15m_trades = trades.resample('15min').agg({
        'vol': 'sum'})
    resample_15m_trades['#trades'] = trades.resample('15min').size()

    etf_data = pd.merge(resample_15m_quotes, resample_15m_trades, how='inner', left_index=True,
                        right_index=True)

    return etf_data


etf = list(map(lambda i: etf_cal(pd.read_pickle(f'/projects/illinois/aces/shared/ruchuan2/SP500/spy_nbbo/{etf_quotes[i]}', compression='gzip'),
                                 pd.read_pickle(f'/projects/illinois/aces/shared/ruchuan2/SP500/spy_trades/{etf_trades[i]}', compression='gzip')),
               range(len(etf_quotes))))

etf = pd.concat(etf)
print('etf finished')
print(len(etf))

market_data = pd.merge(futures, etf, how='inner',
                       left_index=True, right_index=True, suffixes=('_emini', '_spy'))


market_data.to_pickle(
    '/projects/illinois/aces/shared/ruchuan2/SP500/market_data.pkl')
