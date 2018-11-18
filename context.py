import pandas as pd
import numpy as np
from datetime import date

class Context:
    def __init__(self,
                 mktdata: pd.DataFrame, #TODO: pass separate mktdata in for spot so no dupes
                 startdate: date=None,
                 balance: float=0,
                 daysInYear: int=360,
                 rate: float=0.01,
                 ):
        self.mktdata, self.balance, self.daysInYear, self.rate = mktdata, balance, daysInYear, rate
        self.date = startdate or np.min(mktdata['Date'])

    def spot(self, stock: str): #TODO: ideally should be able to call price on any asset class
        """

        """
        md = self.mktdata
        res = md[
            (md['Date'] == pd.Timestamp(self.date)) &
            (md['Stock'] == stock)
        ].reset_index()
        return res.at[0, 'Spot']


    def vol(self, stock: str, maturity: date): #TODO: ideally should be able to call price on any asset class
        """

        TODO: interpolate??
        """
        md = self.mktdata
        res = md[
            (md['Date'] == pd.Timestamp(self.date)) &
            (md['Stock'] == stock) &
            (md['Maturity'] == pd.Timestamp(maturity))
        ].reset_index()
        return res.at[0, 'Volatility']