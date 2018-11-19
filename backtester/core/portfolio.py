import logging
import numpy as np
import pandas as pd
from backtester.core.option_pricer import delta, OPTION_TYPE_CALL
from datetime import date
from backtester.core.context import Context

INDEX = ['Stock', 'Strike', 'Maturity', 'PutCall']
POSITION_COLS = ['Amount']
PRICING_COLS = ['Spot', 'Strike', 'TimeToMaturity', 'Rate', 'Volatility', 'PutCall', 'Amount']
#TRANSACTION_COLS = INDEX

class OptionsPortfolio:
    def __init__(self, context:Context):
        self.context = context
        self.dfPositions = pd.DataFrame(
            columns=INDEX+POSITION_COLS,
        ).set_index(INDEX)
        self.dfPositions['Amount'] = self.dfPositions['Amount'].astype(np.float64) #HACK this is so ugly. no way to create empty dataframe with types!!!

        self.logger = logging.getLogger(__name__)


    def executeTradeByCash(self, cashAmount: float, *args, **kwargs):
        """
        Convenience Wrapper function over executeTrade() to
        """
        price = self.context.optionPrice(*args[:4])
        amount = cashAmount/price
        self.executeTrade(amount, *args, price=price)


    def executeTrade(self,
            amount: float,
            stock: str,
            strike: float,
            maturity: date,
            putcall: int, #OPTION_TYPE_CALL  OPTION_TYPE_PUT
            price: float=None,
    ):

        index = (stock, strike, maturity, putcall)
        self.dfPositions.loc[index, 'Amount'] = \
            self.dfPositions.loc[index, 'Amount'] + amount \
        if index in self.dfPositions \
            else amount

        ctx = self.context
        price = price or ctx.optionPrice(stock, strike, maturity, putcall)

        putcallstr = 'call' if putcall == OPTION_TYPE_CALL else 'put'
        self.logger.info(f'{ctx.date}: trading option: {amount} of {maturity} {strike} {putcallstr} on {stock} for  @ {price}')

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

    def positionsDelta(self): #TODO: calculate all greeks
        paramsDf = self.dfPositionsAugmented()
        paramsDf['Delta'] = delta(*self._pricingParams())
        self.logger.info('deltas: %s' % paramsDf)
        return paramsDf

    def delta(self):
        return self.positionsDelta().groupby('Stock')['Delta'].sum()

    def settleOptions(self):
        ctx = self.context
        maturityStr = ctx.date.strftime('%Y-%m-%d')
        dfExpired = self.dfPositions.query(f"Maturity == '{maturityStr}'")
        if not dfExpired.empty:
            mktdata = ctx.mktdata[['Stock', 'Date', 'Spot']].drop_duplicates()
            joined = pd.merge(dfExpired.reset_index(), mktdata, left_on=['Stock', 'Maturity'], right_on=['Stock', 'Date'])

            joined['Moniness'] = joined.eval("Amount * PutCall * (Spot - Strike)")
            joined['Settlement'] = np.where(joined['Amount'] > 0, np.maximum(0, joined['Moniness']), np.minimum(0, joined['Moniness']))
            self.logger.info(f'{ctx.date}: expiring options\n{joined}')
            ctx.balance -= joined['Settlement'].sum()

            #delete expired options
            self.dfPositions = self.dfPositions.query(f"Maturity > '{maturityStr}'")

    def handleEvent(self):
        self.settleOptions()