def checkForNulls(df):
    nulls = df.isnull()
    if nulls.values.any():
        raise RuntimeError(f'found unexpected nulls \n{nulls}')