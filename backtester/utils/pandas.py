import numpy as np
from datetime import date
from bisect import bisect_left

def checkForNulls(df):
    nulls = df.isnull()
    if nulls.values.any():
        raise RuntimeError(f'found unexpected nulls \n{nulls}')

def getNearestNextDay(inDate, sortedDates):
    """
    given a Series of sorted dates, Rolls the input date forward if it's not in that list.
    Really bad HACK because I can't get pd.CustomBusinessDate take a Series calendar of dates
    """
    index = bisect_left(sortedDates, np.datetime64(inDate))
    return sortedDates[index]