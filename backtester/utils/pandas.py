import pandas as pd

def checkForNulls(df: pd.DataFrame):
    nulls = df.isnull()
    if nulls.values.any():
        raise RuntimeError(f'found unexpected nulls \n{nulls}')