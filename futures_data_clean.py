# -*- coding: utf-8 -*-
"""
Created on Mon May  5 13:34:33 2025
Cleaning the CME market trades and depth data
@author: ruchuan2
"""

import pandas as pd
import pyreadr
import os

# read R rda file

files = os.listdir(
    '/projects/illinois/aces/shared/ruchuan2/SP500/front_month_book/')

for i in range(len(files)):

    futures_quotes = pyreadr.read_r(
        f'/projects/illinois/aces/shared/ruchuan2/SP500/front_month_book/{files[i]}')

    futures_quotes = list(futures_quotes.values())[0]

    # market close and open
    trading_day = futures_quotes['Date'].unique()[0]

    market_open = pd.to_datetime(f'{trading_day} 09:30')
    market_open = market_open.tz_localize('America/New_York')
    market_close = pd.to_datetime(f'{trading_day} 16:00')
    market_close = market_close.tz_localize('America/New_York')

    print(trading_day)

    futures_quotes['Time'] = futures_quotes['Time'].astype('str')

    # break timestamps into parts

    futures_quotes['Time'] = futures_quotes['Time'].str.slice(0, 8) + " " + futures_quotes['Time'].str.slice(8, 14) + '.' +\
        futures_quotes['Time'].str.slice(14, 25)

    futures_quotes['Time'] = pd.to_datetime(
        futures_quotes['Time'], format="%Y%m%d %H%M%S.%f", utc=True)
    futures_quotes['Time'] = futures_quotes['Time'].dt.tz_convert(
        'America/New_York')
    futures_quotes = futures_quotes.loc[(futures_quotes['Time'] >= market_open) &
                                        (futures_quotes['Time'] <= market_close)].reset_index(drop=True)

    futures_quotes = futures_quotes.filter(regex=r'Time|PX|Qty')

    futures_quotes.to_pickle(
        f'/projects/illinois/aces/shared/ruchuan2/SP500/front_month_book_cleaned/{trading_day}.pkl', compression='gzip')
