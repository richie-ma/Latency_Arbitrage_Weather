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
    '/projects/illinois/aces/shared/ruchuan2/SP500/spy_nbbo_rda/')

for i in range(len(files)):

    spy_quotes = pyreadr.read_r(
        f'/projects/illinois/aces/shared/ruchuan2/SP500/spy_nbbo_rda/{files[i]}')

    spy_quotes = list(spy_quotes.values())[0]
    spy_quotes.to_pickle(
        f'/projects/illinois/aces/shared/ruchuan2/SP500/spy_nbbo/{files[i]}.pkl', compression='gzip')
