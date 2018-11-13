# -*- coding: utf-8 -*-
"""
Created on Tue Nov 13 13:57:49 2018

@author: Administrator
"""

import pandas as pd
import numpy as np

filaname = r'C:\Users\Administrator\PycharmProjects\backtester\data\spx_vols.txt'

df = pd.read_csv(filaname, parse_dates=['Date', 'Maturity']) # dtype={'Date': np.datetime64, 'Maturity': np.datetime64})
df['Maturity'] = pd.to_datetime(df['Maturity'], format='%Y%m%d')

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