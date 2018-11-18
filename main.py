from context import Context
from datetime import date
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

def _groupbyInterpFunc(data):
    return interp1d(data['DaysToMaturity'], data['Volatility'], bounds_error=False, fill_value='extrapolate', kind='cubic')

def getMktData():
    filaname = r'C:\Users\Administrator\PycharmProjects\backtester\data\spx_vols.txt'

    df = pd.read_csv(filaname, parse_dates=['Date', 'Maturity']) # dtype={'Date': np.datetime64, 'Maturity': np.datetime64})
    df['Maturity'] = pd.to_datetime(df['Maturity'], format='%Y%m%d')
    df['DaysToMaturity'] = (df['Maturity'] - df['Date']).astype('timedelta64[D]') #TODO: check whether using day instead of business day to interpolate is correct?

    dfGroupedByInterp = pd.DataFrame(df.groupby(['Date', 'Spot']).apply(_groupbyInterpFunc))
    interpFuncDict = dfGroupedByInterp.to_dict('index')
    daysToMaturity = np.array(range(3,85))
    interpDict = {k: v[0](daysToMaturity) for k,v in interpFuncDict.items()}
    listOfDfs = [pd.DataFrame({'Date': k[0], 'Spot': k[1], 'DaysToMaturity':daysToMaturity, 'Volatility':v}) for k,v in interpDict.items()]
    dfInterpolatedVols = pd.concat(listOfDfs)
    dfInterpolatedVols['Maturity'] = dfInterpolatedVols['Date'] + pd.to_timedelta(dfInterpolatedVols['DaysToMaturity'],                                                                                  unit='d')
    dfInterpolatedVols['Symbol'] = 'SPY'

    return dfInterpolatedVols

if __name__ == '__main__':
    mktdata = getMktData()
    context = Context(mktdata)

    print(
        context.vol('SPY', date(2013, 4, 1))
    )