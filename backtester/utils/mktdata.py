import pandas as pd
import numpy as np
from scipy.interpolate import interp1d


def _groupbyInterpFunc(data):
    return interp1d(data['DaysToMaturity'], data['Volatility'], bounds_error=False, fill_value='extrapolate', kind='cubic')

def readMktData(filaname):
    """
    TODO: This custom funciton should probably not belong here
    """
    df = pd.read_csv(filaname, parse_dates=['Date', 'Maturity']) # dtype={'Date': np.datetime64, 'Maturity': np.datetime64})
    df['Maturity'] = pd.to_datetime(df['Maturity'], format='%Y%m%d')
    df['DaysToMaturity'] = (df['Maturity'] - df['Date']).astype('timedelta64[D]') #TODO: check whether using day instead of business day to interpolate is correct?
    return df

def createVolSurface(df):
    dfGroupedByInterp = pd.DataFrame(df.groupby(['Date', 'Spot']).apply(_groupbyInterpFunc))
    interpFuncDict = dfGroupedByInterp.to_dict('index')
    daysToMaturity = np.array(range(1,91))
    interpDict = {k: v[0](daysToMaturity) for k,v in interpFuncDict.items()}
    listOfDfs = [pd.DataFrame({'Date': k[0], 'Spot': k[1], 'DaysToMaturity':daysToMaturity, 'Volatility':v}) for k,v in interpDict.items()]
    dfInterpolatedVols = pd.concat(listOfDfs)
    dfInterpolatedVols['Maturity'] = dfInterpolatedVols['Date'] + pd.to_timedelta(dfInterpolatedVols['DaysToMaturity'],                                                                                  unit='d')
    dfInterpolatedVols['Stock'] = '.SPX'

    return dfInterpolatedVols