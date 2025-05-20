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

# correlation breakdown
# Oct 22, 2018 as an example

spy = pd.read_pickle(
    "C:/Users/ruchuan2/Box/latency_arbitrage/20180806_spy.pkl", compression='gzip')
futures = pd.read_pickle(
    "C:/Users/ruchuan2/Box/latency_arbitrage/20180806_futures.pkl", compression='gzip')

# daily

spy['Time'] = pd.to_timedelta(
    spy['time_m'], unit='s') + pd.to_datetime(spy['date'])
spy['Time'] = pd.to_datetime(spy['Time'])
spy['Time'] = spy['Time'].dt.tz_localize('America/New_York')
spy.drop(spy[(spy['bid'] == 0) | (
    spy['ask'] == 0)].index, inplace=True)
spy.drop(spy[spy['bid'] >= spy['ask']].index,
         inplace=True)

spy['midpoint'] = (spy['bid']+spy['ask'])/2*10
futures.drop(futures[(futures['Bid_PX_1'] == 0) | (futures['Ask_PX_1'] == 0)].index,
             inplace=True)

futures.drop(futures[futures['Bid_PX_1'] >= futures['Ask_PX_1']].index,
             inplace=True)
futures['midpoint'] = (futures['Bid_PX_1'] + futures['Ask_PX_1'])/2

merged_data = pd.merge_asof(futures[['Time', 'midpoint']], spy[['Time', 'midpoint']],
                            suffixes=('_e-mini', '_spy'), left_on='Time', right_on='Time').ffill()
merged_data = merged_data.dropna()


# one hour
start = pd.to_datetime('10:00').time()
end = pd.to_datetime('10:59').time()

merged_1h = merged_data[(merged_data['Time'].dt.time >= start)
                        & (merged_data['Time'].dt.time <= end)]
# merged_1h = pd.melt(merged_1h, id_vars='Time', value_vars=['midpoint_e-mini', 'midpoint_spy'],
#                    var_name='market', value_name='midpoint')

# 1minute

start = pd.to_datetime('11:00').time()
end = pd.to_datetime('11:01').time()

merged_1m = merged_data[(merged_data['Time'].dt.time >= start)
                        & (merged_data['Time'].dt.time <= end)]
# merged_1m = pd.melt(merged_1m, id_vars='Time', value_vars=['midpoint_e-mini', 'midpoint_spy'],
#                    var_name='market', value_name='midpoint')

# 30s

start = pd.to_datetime('09:31:00').time()
end = pd.to_datetime('09:31:30').time()

merged_30s = merged_data[(merged_data['Time'].dt.time >= start)
                         & (merged_data['Time'].dt.time <= end)]
# merged_250ms = pd.melt(merged_250ms, id_vars='Time', value_vars=['midpoint_e-mini', 'midpoint_spy'],
#                       var_name='market', value_name='midpoint')
# merged_data = pd.melt(merged_data, id_vars='Time', value_vars=['midpoint_e-mini', 'midpoint_spy'],
#                      var_name='market', value_name='midpoint')

# figures
fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.plot(merged_data['Time'], merged_data['midpoint_e-mini'],
         label='E-mini', color='blue')
ax1.set_ylabel("E-mini mipoint price", color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# Create right axis for SPY
ax2 = ax1.twinx()
ax2.plot(merged_data['Time'], merged_data['midpoint_spy'],
         label='SPY', color='green')
ax2.set_ylabel("SPY midpoint price * 10", color='green')
ax2.tick_params(axis='y', labelcolor='green')

plt.title("Day")
plt.xlabel("Time")
plt.ylabel("Midpoint price")

# Combined legend
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')


fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.plot(merged_1h['Time'], merged_1h['midpoint_e-mini'],
         label='E-mini', color='blue')
ax1.set_ylabel("E-mini mipoint price", color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# Create right axis for SPY
ax2 = ax1.twinx()
ax2.plot(merged_1h['Time'], merged_1h['midpoint_spy'],
         label='SPY', color='green')
ax2.set_ylabel("SPY midpoint price * 10", color='green')
ax2.tick_params(axis='y', labelcolor='green')

plt.title("Hour")
plt.xlabel("Time")
plt.ylabel("Midpoint price")
# Combined legend
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')


fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.plot(merged_1m['Time'], merged_1m['midpoint_e-mini'],
         label='E-mini', color='blue')
ax1.set_ylabel("E-mini mipoint price", color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# Create right axis for SPY
ax2 = ax1.twinx()
ax2.plot(merged_1m['Time'], merged_1m['midpoint_spy'],
         label='SPY', color='green')
ax2.set_ylabel("SPY midpoint price * 10", color='green')
ax2.tick_params(axis='y', labelcolor='green')

plt.title("Minute")
plt.xlabel("Time")
plt.ylabel("Midpoint price")
# Combined legend
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

fig, ax1 = plt.subplots(figsize=(10, 6))
ax1.plot(merged_30s['Time'], merged_30s['midpoint_e-mini'],
         label='E-mini', color='blue')
ax1.set_ylabel("E-mini mipoint price", color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# Create right axis for SPY
ax2 = ax1.twinx()
ax2.plot(merged_30s['Time'], merged_30s['midpoint_spy'],
         label='SPY', color='green')
ax2.set_ylabel("SPY midpoint price * 10", color='green')
ax2.tick_params(axis='y', labelcolor='green')

plt.title("30s")
plt.xlabel("Time")
plt.ylabel("Midpoint price")
# Combined legend
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

# Create right axis for SPY
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
