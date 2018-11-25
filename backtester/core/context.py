import pandas as pd
import numpy as np
from datetime import date, timedelta
from backtester.utils.pandas import generateHolidays
from pandas.tseries.offsets import CustomBusinessDay
import logging

class Context:
    def __init__(self,
                 mktdata: pd.DataFrame, #TODO: pass separate mktdata in for spot so no dupes
                 startdate: date=None,
                 enddate: date=None,
                 balance: float=0,
                 rate: float=0.01,
                 ):
        self.mktdata, self.balance, self.rate = mktdata, balance, rate
        self.date = startdate or mktdata['Date'].min()
        self.enddate = enddate or mktdata['Date'].max()
        self.logger = logging.getLogger(__name__)

        self.businessdays = mktdata['Date'].unique()
        holidays = generateHolidays(self.businessdays) #HACK should really use a holiday calendar
        self.businessday = pd.tseries.offsets.CustomBusinessDay(holidays=holidays)

    def spots(self):
        """
        Today's Spot for all stock
        """
        md = self.mktdata.reset_index()
        res = md[
            md['Date'] == pd.Timestamp(self.date)
        ][['Stock', 'Spot']].drop_duplicates('Stock')
        return res

    def spot(self, stock: str):
        """
        Today's Spot for a given Stock
        """
        md = self.spots()
        res = md[md['Stock'] == stock]
        if len(res) != 1:
            raise RuntimeError(f'{self.date}: filtered DF should only have 1 row found {len(res)}\n{res}')

        return res.reset_index().at[0, 'Spot'] #TODO: how to select first element without reset_index?


    def vol(self, stock: str, maturity: date):
        """

        Today's Vol for a given Stock, Maturity (flat across strike)
        """
        md = self.mktdata
        res = md[
            (md['Date'] == pd.Timestamp(self.date)) &
            (md['Stock'] == stock) &
            (md['Maturity'] == pd.Timestamp(maturity))
        ]
        return res.reset_index().at[0, 'Volatility'] #TODO: how to select first element without reset_index?

    def isTradingDay(self):
        #TODO: use calendar instead of looking at mktdata
        return np.datetime64(self.date) in self.businessdays

    def nextEvent(self):
        """
        HACK for now but could be extended in future to accept events from a pipeline
        :return: False when no moer events
        """

        self.date += timedelta(days=1)
        if self.date > self.enddate:
            return False

        return True
