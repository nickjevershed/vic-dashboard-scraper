#!/usr/bin/env python3

import pandas as pd
import requests
from datetime import datetime, timedelta
import numpy as np
from syncData import syncData

#%%

test = ""
# test = "-test"

cols = ['row', 'lga', 'state', 'date', 'cases']

print("Getting data..")

json = requests.get('https://interactive.guim.co.uk/covidfeeds/victoria-export.json').json()
df = pd.DataFrame(json)

#%%

df.columns = cols
df.date = pd.to_datetime(df.date, format="%Y-%m-%d")
df = df.set_index('date')
df = df.sort_index(ascending=1)
df['cases'] = pd.to_numeric(df['cases'])

lastUpdated = df.index[-1]
four_weeks_ago = lastUpdated - timedelta(days=28)

short = df[four_weeks_ago:]

short_p = short.pivot(columns='lga', values='cases')

lga_daily = pd.DataFrame()

for col in short_p.columns:
	tempSeries = short_p[col].dropna()
	tempSeries = tempSeries.sub(tempSeries.shift())
# 	tempSeries.iloc[0] = short_p[col].dropna().iloc[0]
	lga_daily = pd.concat([lga_daily, tempSeries], axis=1)

# lga_daily = lga_daily[:-2]

last_row = lga_daily[-1:].squeeze()
allZeroes = True
for index, value in last_row.items():
	if value != 0:
		allZeroes = False
		break
if allZeroes:
	lga_daily = lga_daily[:-1]

two_weeks_ago = lga_daily.index[-1] - timedelta(days=13)

totals = lga_daily[two_weeks_ago:].sum()

totals = totals[totals >= 5]

lga_daily.to_csv('lga_daily.csv')

one_week_ago = lga_daily.index[-1] - timedelta(days=6)

#%%

no_negs = lga_daily

no_negs[no_negs < 0] = 0

rolling = no_negs.rolling(7).mean()
rolling.to_csv("rolling.csv")
lga_movement = []

for col in totals.index:
	print(col)
	row = {}
	row['lga'] = col
	row['change'] = rolling.loc[lga_daily.index[-1], col] - rolling.loc[one_week_ago, col]
	row['this_week'] = lga_daily[one_week_ago:][col].sum()
	row['last_week'] = lga_daily[two_weeks_ago:one_week_ago - timedelta(days=1)][col].sum()
	row['weekly_change'] = 	row['this_week'] - row['last_week']
	row['date'] = lga_daily.index[-1].strftime('%Y-%m-%d')
	lga_movement.append(row)

lga_df_movement1 = pd.DataFrame(lga_movement)


#%%

syncData(lga_movement,'2020/07/vic-corona-map{test}'.format(test=test), "vicChange-2")
	
# short['rolling_mean'] = df.groupby('lga')['cases'].transform(lambda x: x.rolling(7, 1).mean())


