import pandas as pd

def checkForNulls(df):
    nulls = df.isnull()
    if nulls.values.any():
        raise RuntimeError(f'found unexpected nulls \n{nulls}')


def generateHolidays(timeSeries):
    """

    Generates a list of weekday holes (holidays) from a timeseries
    """
    busdaytimeseries = pd.Series(timeSeries)
    daterange = pd.date_range(start=busdaytimeseries.min(), end=busdaytimeseries.max(), freq='B')
    holidays = daterange.difference(busdaytimeseries)
    return holidays