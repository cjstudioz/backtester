import logging
import pandas as pd
from option_pricer import delta, optionPrice
from datetime import date
from context import Context

INDEX = ['Stock', 'Strike', 'Maturity', 'PutCall']
POSITION_COLS = ['Amount']
PRICING_COLS = ['Spot', 'Strike', 'TimeToMaturity', 'Rate', 'Volatility', 'PutCall', 'Amount']
#TRANSACTION_COLS = INDEX

class OptionsPortfolio:
    def __init__(self, context:Context):
        self.context = context
        self.dfPositions = pd.DataFrame(columns=INDEX+POSITION_COLS).set_index(INDEX)
        self.logger = logging.getLogger(__name__)


    def executeTradeByCash(self, stock: str, cashAmount: float, *args, **kwargs):
        """
        Convenience Wrapper function over executeTrade() to
        """
        price = self.context.optionPrice(stock, strike, maturity, putcall)
        amount = cashAmount/price
        self.executeTrade(stock, amount, *args, price=price)


    def executeTrade(self,
            stock: str,
            amount: float,
            strike: float,
            maturity: date,
            putcall: int, #option_pricer.OPTION_TYPE_CALL  OPTION_TYPE_PUT
            price: float=None,
    ):

        index = (stock, strike, maturity, putcall)
        self.dfPositions.loc[index, 'Amount'] = \
            self.dfPositions.loc[index, 'Amount'] + amount \
        if index in self.dfPositions \
            else amount

        ctx = self.context
        price = price or ctx.optionPrice(stock, strike, maturity, putcall)

        self.logger.info(f'trading option: {amount} of {stock} @ {price}')

        ctx.balance -= price * amount

        # self.dfTransactions.append([
        #     [self.context.date, stock, strike, maturity, price, amount]
        # ])

    def dfPositionsAugmented(self):
        # TODO: memoize this
        ctx = self.context
        joinkey = ['Stock', 'Maturity']
        mktdata = ctx.mktdata.set_index(joinkey)
        joined = self.dfPositions.join(
            mktdata[mktdata['Date'] == pd.Timestamp(self.context.date)], on=joinkey
        ).reset_index()
        joined['TimeToMaturity'] = (joined['Maturity'] - ctx.date).dt.days / ctx.daysInYear
        joined['Rate'] = ctx.rate

        self.logger.debug(f'pricing params: {joined}')
        if joined.isnull().values.any():
            raise RuntimeError('found unexpected nulls \n%s' % joined.isnull())

        return joined

    def _pricingParams(self):
        augm = self.dfPositionsAugmented()
        res = augm[PRICING_COLS].values.transpose()
        return res

    def positionsDelta(self):
        paramsDf = self.dfPositionsAugmented()
        paramsDf['Delta'] = delta(*self._pricingParams())
        self.logger.info('deltas: %s' % paramsDf)
        return paramsDf

    def delta(self):
        return self.positionsDelta().groupby('Stock')['Delta'].sum()

    def settleOptions(self):
        settlement = 0
        expiredOptions = [v for v in self.options.values() if v.isExpired()]

        if expiredOptions:
            settlement = sum(option.moniness for option in expiredOptions)
            self.options = {k: v for k, v in self.options.iteritems() if not v.isExpired()}

        return settlement