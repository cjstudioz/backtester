import pandas as pd
from option_pricer import delta, OPTION_TYPE_CALL, OPTION_TYPE_PUT

INDEX = ['Underlying', 'Strike', 'Maturity', 'PutCall']
POSITION_COLS = ['Amount']
#TRANSACTION_COLS = INDEX

class Portfolio():
    def __init(self, context):
        self.context = context
        self.dfPositions = pd.DataFrame(columns=INDEX+COLUMNS).set_index(INDEX)


    def executeTrade(self,
            underlying: str,
            strike: double,
            maturity: date,
            putcall: int, #option_pricer.OPTION_TYPE_CALL  OPTION_TYPE_PUT
            price: double,
            amount: double,
    ):

        index = (underlying, strike, maturity, putcall)
        self.dfPositions.loc[index, 'Amount'] = \
            self.dfPositions.loc[index, 'Amount'] + amount \
        if index in self.dfPositions \
            else amount

        self.context.balance -= price * amount

        # self.dfTransactions.append([
        #     [self.context.date, underlying, strike, maturity, price, amount]
        # ])




    def delta(self, underlying:str):
        ctx = self.context
        deltaRaw = delta(
            ctx.spot(underlying),
            self.dfPositions['Strike'],
            (self.dfPositions['Maturity'] - ctx.date).days / ctx.DAYS_IN_YEAR,
            ctx.rate,
            ctx.vol(underlying),
            self.dfPositions['PutCall']
        )

        return deltaRaw.sum()

    def settleOptions(self):
        settlement = 0
        expiredOptions = [v for v in self.options.values() if v.isExpired()]

        if expiredOptions:
            settlement = sum(option.moniness for option in expiredOptions)
            self.options = {k: v for k, v in self.options.iteritems() if not v.isExpired()}

        return settlement