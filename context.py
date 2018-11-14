import pandas as pd
from datetime import date

class Context():
    def __init__(self, mktdata: pd.DataFrame, startdate: date=None):
        self.mktdata = mktdata #TODO: pass separate mktdata in for spot so no dupes
        self.date = startdate or np.min(mktdata['date'])

    def spot(self, symbol: str): #TODO: ideally should be able to call price on any asset class
        """

        """
        return self.mktdata.query(f"""
            Date == {self.date}                                  
            & Symbol == {symbol}            
        """).at[0, 'Spot']

    def atmvol(self, symbol: str): #TODO: ideally should be able to call price on any asset class
        """

        TODO: interpolate??
        """
        return self.mktdata.query(f"""
            Date == {self.date}                                  
            & Symbol == {symbol}
            & Symbol == {symbol}            
        """).at[0, 'Volatility']