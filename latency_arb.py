# -*- coding: utf-8 -*-
"""
Created on Fri May  9 16:31:19 2025

latency arbitrage under precipitation
We identify Ã¢â‚¬Å“standalone signalsÃ¢â‚¬Â as trades in the futures market separated 
by at least 10 milliseconds from the previous trade, which helps isolate independent trading
decisions rather than split orders.

@author: ruchuan2
"""
import pandas as pd
import numpy as np
import os


# aggregate trades with the sametimestamp and direction
# 1 buyer initiated and 2 seller initiated

def latency_arb(futures_trades, etf_trades, etf_quotes):

    print(futures_trades['Time'].dt.date.unique(), flush=True)

    futures_trades['agg'] = np.where(futures_trades['agg'] == 1, 1, -1)

    futures_trades = futures_trades[['Time', 'PX', 'Size', 'agg']]
    futures_trades = futures_trades.groupby(
        ['Time', 'PX', 'agg'], as_index=False)
    futures_trades = futures_trades.sum()

    futures_trades['time_diff'] = futures_trades['Time'].shift(
        -1) - futures_trades['Time']
    futures_trades['time_diff'] = futures_trades['time_diff'].dt.total_seconds()

    etf_trades['Time'] = pd.to_timedelta(
        etf_trades['time_m'], unit='s') + pd.to_datetime(etf_trades['date'])
    etf_trades['Time'] = pd.to_datetime(etf_trades['Time'])
    etf_trades['Time'] = etf_trades['Time'].dt.tz_localize(
        'America/New_York')
    etf_trades = etf_trades[['Time', 'price', 'size', 'ex']]

    etf_quotes['Time'] = pd.to_timedelta(
        etf_quotes['time_m'], unit='s') + pd.to_datetime(etf_quotes['date'])
    etf_quotes['Time'] = pd.to_datetime(etf_quotes['Time'])
    etf_quotes['Time'] = etf_quotes['Time'].dt.tz_localize(
        'America/New_York')

    # delte observations with time diffrence less than 10 milliseconds

    futures_trades.drop(
        futures_trades[futures_trades['time_diff'] < 0.01].index, inplace=True)

    # assign trades by Lee and Ready (1991)

    etf_quotes = etf_quotes[['Time', 'bid', 'ask']]
    etf_quotes = etf_quotes.copy()
    etf_quotes['midpoint'] = (etf_quotes['ask'] + etf_quotes['bid'])/2

    etf_trades = pd.merge_asof(etf_trades, etf_quotes[['Time', 'midpoint']], on='Time',
                               direction='backward')
    etf_trades.drop(
        etf_trades.loc[etf_trades['midpoint'].isna()].index, inplace=True)
    # find the first trade that is not 0

    etf_trades['agg'] = np.where(etf_trades['price'] > etf_trades['midpoint'], 1,
                                 np.where(etf_trades['price'] < etf_trades['midpoint'], -1, 0))

    first_trade = int(etf_trades.loc[etf_trades['agg'] != 0].index[0])

    etf_trades = etf_trades.loc[etf_trades.index >= first_trade]

    date = futures_trades['Time'].dt.date.unique()[0]

    while True:

        if 0 in etf_trades.loc[etf_trades['agg'] == 0, 'agg'].index:
            break

        etf_trades['agg'] = np.where((etf_trades['agg'] == 0) & (
            etf_trades['agg'].shift(1) == 1), 1,
            np.where((etf_trades['agg'] == 0) & (etf_trades['agg'].shift(1) == -1), -1, etf_trades['agg']))

        if etf_trades.loc[etf_trades['agg'] == 0, 'agg'].count() == 0:
            break

    # finding corresponding etf trades by merging data
    del futures_trades['time_diff']

    def latency_arb_main(futures_trades, etf_trades):

        futures_time = futures_trades.reset_index(drop=True)['Time']
        futures_agg = futures_trades.reset_index(drop=True)['agg']

        results = []

        for i in range(len(futures_time)):

            #print(futures_time[i])

            freq = ['5ms', '6ms', '7ms', '8ms', '9ms', '10ms']

            single_results = []

            for k in range(len(freq)-1):

                start = futures_time[i]+pd.Timedelta(freq[k])
                end = futures_time[i]+pd.Timedelta(freq[k+1])

                # check trading direction

                etf_trd = etf_trades.loc[(etf_trades['Time'] >= start) & (
                    etf_trades['Time'] < end) & etf_trades['agg'] == futures_agg[i]]

                if not etf_trd.empty:
                    vol = sum(etf_trd['price']*etf_trd['size'])/10**6
                    num_trades = etf_trd['price'].count()

                else:

                    vol = 0
                    num_trades = 0

                single_results.append({
                    'freq': f'[{freq[k]}, {freq[k+1]})',
                    'vol': vol,
                    '#trades': num_trades
                })

            single_results = pd.DataFrame(single_results)
            single_results['Time'] = futures_time[i]

            results.append(single_results)

        results = pd.concat(results)
        results = results.groupby(['Time','freq']).sum()
        results = results.reset_index()
        results = results.set_index('Time')
        results = results.groupby('freq').resample('15min').agg({'vol': 'sum', '#trades': 'sum'}).reset_index()

        return results

    arb_results = latency_arb_main(futures_trades, etf_trades)
    if not arb_results.empty:
        arb_results.to_pickle(
            f'/projects/illinois/aces/shared/ruchuan2/SP500/latency_arb/{date}.pkl')


