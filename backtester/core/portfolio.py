import logging
import numpy as np
import pandas as pd
from backtester.core import option_pricer
from backtester.utils.pandas import checkForNulls
from datetime import date
from backtester.core.context import Context
from functools import partial

#TRANSACTION_COLS = INDEX

class Portfolio:
    def __init__(self, context: Context):
        self.context = context
        self.dfPositions = pd.DataFrame(
            columns=self.INDEX + self.POSITION_COLS,
        ).set_index(self.INDEX)
        self.dfPositions['Amount'] = self.dfPositions['Amount'].astype(np.float64) #HACK this is so ugly. no way to create empty dataframe with types!!!
        self.dfPositionsHist = []
        
        self.logger = logging.getLogger(__name__)
        

    def executeTradeByCash(self, cashAmount: float, *args, **kwargs):
        """
        Convenience Wrapper function over executeTrade() that given trade notional works out how many units
        """
        price = self.todaysMktPrice(*args)
        amount = cashAmount/price
        self.executeTrade(amount, *args, price=price, **kwargs)

    def executeTradeTargetAmount(self, targetAmt: float, *args, **kwargs):
        """
        Convenience Wrapper function over executeTrade() that given trade notional works out how many units
        """
        indexSize = len(self.INDEX) #HACK: another stupid hack due to dataframe index vs multiindex
        index = args[:indexSize] if indexSize > 1 else args[0]  #TODO: appreciate this is quite brittle. put test around it?
        balance = self.dfPositions.loc[index, 'Amount'].sum() if index in self.dfPositions.index else 0
        amount = targetAmt - balance
        self.executeTrade(amount, *args, **kwargs)

    def executeTrade(self, *args, **kwargs):
        raise NotImplementedError()

    def todaysMktPrice(self, *args):
        raise NotImplementedError()

    def todaysNotional(self, *args):
        raise NotImplementedError()

    def handleEventPre(self):
        pass

    def handleEventPost(self):
        pass


class StockPortfolio(Portfolio):
    INDEX = ['Stock']
    POSITION_COLS = ['Amount']

    def todaysMktPrice(self, *args):
        stock = args[0]
        res = self.context.spot(stock)
        return res

    def positionPrices(self):
        res = pd.merge(
            self.dfPositions.reset_index(),
            self.context.spots(),
        how='left', on=['Stock'])
        res['Price'] = res['Spot'] * res['Amount']

        checkForNulls(res)
        return res


    def notional(self):
        return self.positionPrices()['Price'].sum()

    def executeTrade(self,
                     amount: float,
                     stock: str,
                     price: float= None
                     ):
        """

        TODO: make this atomic?
        TODO: check if balance is > 0?
        """
        ctx = self.context
        self.dfPositions.loc[stock, 'Amount'] = \
            self.dfPositions.loc[stock, 'Amount'] + amount \
                if stock in self.dfPositions \
                else amount

        if price is None:
            price = self.todaysMktPrice(stock)

        self.logger.info(f'{ctx.date}: trading stock: {amount} on {stock} @ {price}')
        ctx.balance -= price * amount

    def handleEventPost(self):
        if self.context.isTradingDay():
            self.dfPositionsHist.append(self.positionPrices())

class OptionsPortfolio(Portfolio):
    INDEX = ['Stock', 'Strike', 'Maturity', 'PutCall']
    POSITION_COLS = ['Amount']
    PRICING_COLS = ['Spot', 'Strike', 'TimeToMaturity', 'Rate', 'Volatility', 'PutCall', 'Amount']
    GREEKS = ['Price', 'Delta', 'Gamma', 'Theta', 'Vega']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #dynamically create greek functions
        for greek in self.GREEKS:
            setattr(self, greek.lower(), partial(self._getGreek, greek=greek))


    def todaysMktPrice(self, *args):
        res = self.context.optionPrice(*args[:4])
        return res

    def notional(self):
        return self.price().sum()

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
        price = price or self.todaysMktPrice(stock, strike, maturity, putcall)

        putcallstr = 'call' if putcall == option_pricer.OPTION_TYPE_CALL else 'put'
        self.logger.info(f'{ctx.date}: trading option: {amount} of {maturity} {strike} {putcallstr} on {stock} @ {price}')

        ctx.balance -= price * amount

        # self.dfTransactions.append([
        #     [self.context.date, stock, strike, maturity, price, amount]
        # ])

    def dfPositionsAugmented(self):
        # TODO: memoize this
        ctx = self.context
        joinkey = ['Stock', 'Maturity']
        mktdata = ctx.mktdata
        joined = pd.merge(
            self.dfPositions.reset_index(),
            mktdata[mktdata['Date'] == pd.Timestamp(self.context.date)],
            how='left', on=['Stock', 'Maturity'],
        )
        joined['TimeToMaturity'] = (joined['Maturity'] - ctx.date).dt.days / ctx.daysInYear
        joined['Rate'] = ctx.rate

        self.logger.debug(f'pricing params: {joined}')
        checkForNulls(joined)
        return joined

    def _pricingParams(self):
        augm = self.dfPositionsAugmented()
        res = augm[self.PRICING_COLS].values.transpose()
        return res

    def positionsGreeks(self): #TODO: calculate all greeks
        paramsDf = self.dfPositionsAugmented()
        for greek in self.GREEKS:
            func = getattr(option_pricer, greek.lower())
            paramsDf[greek] = func(*self._pricingParams())

        return paramsDf

    def _getGreek(self, greek):
        return self.positionsGreeks().groupby('Stock')[greek].sum(axis=1)

    def settleOptions(self):
        ctx = self.context
        maturityStr = ctx.date.strftime('%Y-%m-%d')
        dfExpired = self.dfPositions.query(f"Maturity == '{maturityStr}'")
        if not dfExpired.empty:
            mktdata = ctx.mktdata[['Stock', 'Date', 'Spot']].drop_duplicates()
            joined = pd.merge(dfExpired.reset_index(), mktdata, how='left', left_on=['Stock', 'Maturity'], right_on=['Stock', 'Date'])

            joined['Moniness'] = joined.eval("Amount * PutCall * (Spot - Strike)")
            joined['Settlement'] = np.where(joined['Amount'] > 0, np.maximum(0, joined['Moniness']), np.minimum(0, joined['Moniness']))
            self.logger.info(f'{ctx.date}: expiring options\n{joined}')
            checkForNulls(joined)

            ctx.balance -= joined['Settlement'].sum()

            #delete expired options
            self.dfPositions = self.dfPositions.query(f"Maturity > '{maturityStr}'")

    def handleEventPre(self):
        if self.context.isTradingDay():
            self.settleOptions()

    def handleEventPost(self):
        if self.context.isTradingDay():
            self.dfPositionsHist.append(self.positionsGreeks())
