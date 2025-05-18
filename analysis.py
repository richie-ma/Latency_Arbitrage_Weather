# -*- coding: utf-8 -*-
"""
Created on Sun May 11 14:31:46 2025

regression and latency arbitrage pattern

@author: ruchuan2
"""

import pandas as pd
from tabulate import tabulate
import numpy as np
import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt
import os

market_liquidity_data = pd.read_pickle(
    "C:/Users/ruchuan2/Box/latency_arbitrage/market_data.pkl")

market_liquidity_data.reset_index(inplace=True)
market_liquidity_data = market_liquidity_data.rename(
    columns={'Non_BBO': 'Non_BBO_emini'})

summary_stat = market_liquidity_data.describe()
summary_stat = summary_stat.round(2)

summary_stat = tabulate(summary_stat, headers="keys", tablefmt="github")

# regression about market liquidity and precipitation

weather_data = pd.read_pickle(
    "C:/Users/ruchuan2/Box/latency_arbitrage/weather_data.pkl")

# negative precipitation to zero

weather_data.loc[weather_data['precipitation']
                 < 0, 'precipitation'] = 0

summary = tabulate(weather_data.describe(), headers="keys", tablefmt="github")

weather_data = weather_data.groupby('timestamp', as_index=False)[
    'precipitation'].sum()


weather_data_summary = weather_data.describe()
weather_data_summary = tabulate(
    weather_data_summary, headers="keys", tablefmt="github")

reg_data = pd.merge(weather_data, market_liquidity_data, how='inner', left_on='timestamp',
                    right_on='Time')
reg_data['date'] = reg_data['timestamp'].dt.date
reg_data['rain'] = np.where(reg_data['precipitation'] >= reg_data.groupby(
    'date')['precipitation'].transform(lambda x: 2*np.std(x)), 1, 0)


# fit regression

emini_data = reg_data[['rain', 'spread_emini', 'BBO_emini',
                       'Non_BBO_emini', 'volatility_emini', 'vol_emini', '#trades_emini']]


spy_data = reg_data[['rain', 'spread_spy', 'BBO_spy',
                     'volatility_spy', 'vol_spy', '#trades_spy']]


emini_indepent_vars = emini_data[['rain', 'volatility_emini']]
emini_indepent_vars = sm.add_constant(emini_indepent_vars)

emini_dependent_vars = ['spread_emini', 'BBO_emini',
                        'Non_BBO_emini', 'vol_emini']


def regression(Y, X, data):

    Y = data[Y]
    model = sm.OLS(Y, X).fit()
    summary_df = pd.DataFrame({
        'coef': model.params,
        'std err': model.bse,
        't': model.tvalues,
        'P>|t|': model.pvalues
    }).round(3)
    summary_df = tabulate(summary_df, headers="keys", tablefmt="github")

    return (summary_df)


emini_results = list(map(lambda i: regression(
    emini_dependent_vars[i], emini_indepent_vars, emini_data), range(len(emini_dependent_vars))))


spy_indepent_vars = spy_data[['rain', 'volatility_spy']]
spy_indepent_vars = sm.add_constant(spy_indepent_vars)

spy_dependent_vars = ['spread_spy', 'BBO_spy', 'vol_spy']

spy_results = list(map(lambda i: regression(
    spy_dependent_vars[i], spy_indepent_vars, spy_data), range(len(spy_dependent_vars))))

# latency arbitrage

all_results = sorted(os.listdir(
    "C:/Users/ruchuan2/Box/latency_arbitrage/results"))

latency_arb = []

for i in range(len(all_results)):
    print(i)

    file = f"C:/Users/ruchuan2/Box/latency_arbitrage/results/{all_results[i]}"

    if os.path.getsize(file) != 0:

        arb = pd.read_pickle(file).reset_index()
        latency_arb.append(arb)

latency_arb = pd.concat(latency_arb)


weather_data = pd.read_pickle(
    "C:/Users/ruchuan2/Box/latency_arbitrage/weather_data.pkl")

# negative precipitation to zero

weather_data.loc[weather_data['precipitation']
                 < 0, 'precipitation'] = 0
weather_data = weather_data.groupby('timestamp', as_index=False)[
    'precipitation'].sum()
weather_data['date'] = weather_data['timestamp'].dt.date

latency_arb = pd.merge(weather_data, latency_arb, how='inner',
                       left_on='timestamp', right_on='Time')

latency_arb['rain'] = np.where(latency_arb['precipitation'] >= latency_arb.groupby(
    'date')['precipitation'].transform(lambda x: 3*np.std(x)), 'rain>=3std', 'rain < 3std')


latency_arb['total_vol'] = latency_arb.groupby(
    ['Time'])['vol'].transform('sum')
latency_arb['vol_prop'] = latency_arb['vol']/latency_arb['total_vol']

latency_arb['total_#ntrds'] = latency_arb.groupby(
    ['Time'])['#trades'].transform('sum')
latency_arb['#trds_prop'] = latency_arb['#trades']/latency_arb['total_#ntrds']


sns.barplot(data=latency_arb, x='freq', y='vol', hue='rain')
plt.title("Distribution of Volume by Frequency and Rain Category")
plt.xlabel("Frequency")
plt.ylabel("Volume (million dollars)")
plt.savefig("C:/Users/ruchuan2/Box/latency_arbitrage/volume_boxplot.png", dpi=600)

sns.boxplot(data=latency_arb, x='freq', y='#trades', hue='rain')
plt.title("Distribution of trades by Frequency and Rain Category")
plt.xlabel("Frequency")
plt.ylabel("Number of trades")
plt.savefig("C:/Users/ruchuan2/Box/latency_arbitrage/trades_plot.png", dpi=600)
