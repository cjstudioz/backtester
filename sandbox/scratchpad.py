# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 13:57:49 2018

@author: Administrator
"""

import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import matplotlib

filaname = r'C:\Users\Administrator\PycharmProjects\backtester\data\spx_vols.txt'

df = pd.read_csv(filaname, parse_dates=['Date', 'Maturity']) # dtype={'Date': np.datetime64, 'Maturity': np.datetime64})
df['Maturity'] = pd.to_datetime(df['Maturity'], format='%Y%m%d') #HACK: why doens't parse dates already do this?
df['DaysToMaturity'] = (df['Maturity'] - df['Date']).dt.days  #TODO: check whether using day instead of business day to interpolate is correct?
df['DateDiff'] = np.busday_count(   
    [d.date() for d in df['Date']],
    [d.date() for d in df['Maturity']], 
)

def groupbyInterpFunc(data):
    return interp1d(data['DaysToMaturity'], data['Volatility'], bounds_error=False, fill_value='extrapolate', kind='cubic')

dfGroupedByInterp = pd.DataFrame(df.groupby(['Date', 'Spot']).apply(groupbyInterpFunc))
interpFuncDict = dfGroupedByInterp.to_dict('index')
daysToMaturity = np.array(range(1,92))
interpDict = {k: v[0](daysToMaturity) for k,v in interpFuncDict.items()}
listOfDfs = [pd.DataFrame({'Date': k[0], 'Spot': k[1], 'DaysToMaturity':daysToMaturity, 'Volatility':v}) for k,v in interpDict.items()]
dfInterpolatedVols = pd.concat(listOfDfs)   
dfInterpolatedVols['Maturity'] = dfInterpolatedVols['Date'] + pd.to_timedelta(dfInterpolatedVols['DaysToMaturity'], unit='d')
dfInterpolatedVols['Symbol'] = 'SPY'
 
import pandas as pd
from pandas import DataFrame
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

ax = plt.axes(projection='3d')
ax.scatter3D(
        (dfInterpolatedVols['Date']-min(dfInterpolatedVols['Date'])).astype('timedelta64[D]'), 
dfInterpolatedVols['DaysToMaturity'], dfInterpolatedVols['Volatility'], cmap='Greens')


dfMaturityDays = pd.DataFrame({
    'DaysToMaturity': list(range(1, 91)), 
    '_XProductConstant': 1,
})    
    
dfVols = pd.merge(dfGroupedByInterp, dfMaturityDays, how='outer', on='_XProductConstant')
dfVols['Volatility'] = dfVols.apply(lambda: dfVols['InterpFunc'](dfVols['DaysToMaturity'])
        

df['dateD'] = df['Date'].astype('timedelta64[D])
df['MaturityD'] = df['Maturity'].astype('datetime64[D]')

dfFiltered = df.query('dayCount == 1')

interpFunc = interp1d(dfFiltered['DaysToMaturity'], dfFiltered['Volatility'], kind='cubic')

df['Date_DOW'] = df['Date'].dt.dayofweek
df['Maturity_DOW'] = df['Maturity'].dt.dayofweek


df['DateDiff'] = np.busday_count(   
    [d.date() for d in df['Date']],
    [d.date() for d in df['Maturity']], 
)

dfFiltered = df.query('Date_DOW==4 & DateDiff == 25')

def deltaHedge():
    delta = options.delta()
    purchase = delta - inventory 
    tradeSpot(purchase):
     

deltaHedge()
if context.tradingDate.weekday() == 4:
    option = Option(
        context.spot('SPY'), 
        context.spot('SPY'), 
        context.vol('SPY'), 
    )
    trade()


def expireOptions():
    for option in optionsInventory:
        price = option.strike - context.spot('SPY')
        tradeOption(option, )
    
    {k: v for k, v in optionsInventory.items() if v.maturity <= context

def trade(amount, price):
    account.notional -= amount * price
    positions.append([tradingDate, 'spot', amount, price])