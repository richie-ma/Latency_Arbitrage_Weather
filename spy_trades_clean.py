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
    '/projects/illinois/aces/shared/ruchuan2/SP500/spy_trades/')

for i in range(len(files)):

    spy_trades = pyreadr.read_r(
        f'/projects/illinois/aces/shared/ruchuan2/SP500/spy_trades/{files[i]}')

    spy_trades = list(spy_trades.values())[0]

    spy_trades.to_pickle(
        f'/projects/illinois/aces/shared/ruchuan2/SP500/spy_trades/{files[i]}.pkl', compression='gzip')

