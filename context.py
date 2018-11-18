import pandas as pd
import numpy as np
from datetime import date

class Context:
    def __init__(self, mktdata: pd.DataFrame, startdate: date=None):
        self.mktdata = mktdata #TODO: pass separate mktdata in for spot so no dupes
        self.date = startdate or np.min(mktdata['Date'])

    def spot(self, symbol: str): #TODO: ideally should be able to call price on any asset class
        """

        """
        md = self.mktdata
        res = md[
            (md['Date'] == self.pd.Timestamp(self.date)) &
            (md['Symbol'] == symbol)
        ].reset_index()
        return res.at[0, 'Spot']


    def vol(self, symbol: str, maturity: date): #TODO: ideally should be able to call price on any asset class
        """

        TODO: interpolate??
        """
        md = self.mktdata
        res = md[
            (md['Date'] == pd.Timestamp(self.date)) &
            (md['Symbol'] == symbol) &
            (md['Maturity'] == pd.Timestamp(maturity))
        ].reset_index()
        return res.at[0, 'Volatility']