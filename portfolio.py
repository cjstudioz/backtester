import pandas as pd
from option_pricer import delta, optionPrice
from datetime import date

INDEX = ['Stock', 'Strike', 'Maturity', 'PutCall']
POSITION_COLS = ['Amount']
#TRANSACTION_COLS = INDEX

class OptionsPortfolio():
    def __init__(self, context):
        self.context = context
        self.dfPositions = pd.DataFrame(columns=INDEX+POSITION_COLS).set_index(INDEX)


    def executeTrade(self,
            underlying: str,
            strike: float,
            maturity: date,
            putcall: int, #option_pricer.OPTION_TYPE_CALL  OPTION_TYPE_PUT
            amount: float,
            price: float=None,
    ):

        index = (underlying, strike, maturity, putcall)
        self.dfPositions.loc[index, 'Amount'] = \
            self.dfPositions.loc[index, 'Amount'] + amount \
        if index in self.dfPositions \
            else amount

        ctx = self.context
        price = price or optionPrice(*self._getPricingParams(underlying, dict(
            Strike=strike,
            TimeToMaturity=(maturity - ctx.date).days / ctx.daysInYear,
            PutCall=putcall,
            Volatility=self.context.vol(underlying, maturity),
        )))
        ctx.balance -= price * amount

        # self.dfTransactions.append([
        #     [self.context.date, underlying, strike, maturity, price, amount]
        # ])

    def dfPositionVols(self):
        ctx = self.context
        joinkey = ['Stock', 'Maturity']
        mktdata = ctx.mktdata.set_index(joinkey)
        joined = self.dfPositions.join(
            mktdata[mktdata['Date'] == pd.Timestamp(self.context.date)], on=joinkey
        ).reset_index()
        joined['TimeToMaturity'] = (joined['Maturity'] - ctx.date).dt.days / ctx.daysInYear

        if joined.isnull().values.any():
            raise RuntimeError('found unexpected nulls \n%s' % joined.isnull())

        return joined

    def _getPricingParams(self, underlying:str, optionParams=None):
        optionParams = optionParams or self.dfPositionVols()
        ctx = self.context
        params = [
            ctx.spot(underlying),
            optionParams['Strike'],
            optionParams['TimeToMaturity'],
            ctx.rate,
            optionParams['Volatility'],
            optionParams['PutCall']
        ]
        return params

    def delta(self, underlying:str):
        deltaRaw = delta(*self._getPricingParams(underlying))
        return deltaRaw.sum()

    def settleOptions(self):
        settlement = 0
        expiredOptions = [v for v in self.options.values() if v.isExpired()]

        if expiredOptions:
            settlement = sum(option.moniness for option in expiredOptions)
            self.options = {k: v for k, v in self.options.iteritems() if not v.isExpired()}

        return settlement