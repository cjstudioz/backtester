import logging
import numpy as np
import pandas as pd
from backtester.pricers import black_scholes_option_pricer
from backtester.pricers.option_types import OptionTypes
from backtester.utils.pandas import checkForNulls
from datetime import date
from backtester.core.context import Context
from functools import partial


#TRANSACTION_COLS = INDEX

class Portfolio:
    """
    Abstract base class (though not strictly) do not instantiate this
    """
    def __init__(self, context: Context):
        self.context = context
        self.dfPositions = pd.DataFrame(
            columns=self.INDEX + self.POSITION_COLS,
        ).set_index(self.INDEX)
        self.dfPositions['Amount'] = self.dfPositions['Amount'].astype(np.float64) #HACK this is so ugly. no way to create empty dataframe with types!!!
        self.dfPositionsHist = [] #list of DFs
        self._tradeHist = [] #list of lists
        
        self.logger = logging.getLogger(__name__)
        
    def dfTradeHist(self):
        """
        For Post Sim Reporting build a dataframe trade history list
        """
        res = pd.DataFrame(self._tradeHist, columns=self.TRADE_COLS)
        return res

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

    def handleEventPre(self):
        pass

    def handleEventPost(self):
        pass


class FuturesPortfolio(Portfolio):
    """
    Naive implementation of a CFD with no interest. assumes no margin required and still able to trade in and out of position with 0 or less cash balance.
    """

    INDEX = ['Stock']
    POSITION_COLS = ['Amount', 'PreviousSpot']
    TRADE_COLS=['Date'] + INDEX + ['Amount', 'Price']

    def todaysMktPrice(self, *args):
        stock = args[0]
        res = self.context.spot(stock)
        return res

    def marginPnL(self):
        if not self.dfPositions.empty:
            res = pd.merge(
                self.dfPositions.reset_index(),
                self.context.spots(),
            how='left', on=['Stock'])
            res['Date'] = self.context.date
            res['PnL'] = (res['Spot'] - res['PreviousSpot']) * res['Amount']

            checkForNulls(res)
            return res

    def executeTrade(self,
                     amount: float,
                     stock: str,
                     ):
        """

        TODO: make this atomic?
        TODO: check if balance is > 0?
        """
        ctx = self.context
        price = ctx.spot(stock)
        self.logger.info(f'{ctx.date}: trading stock: {amount} on {stock} @ {price}')

        self.dfPositions.loc[stock, 'Amount'] = \
            self.dfPositions.loc[stock, 'Amount'] + amount \
                if stock in self.dfPositions.index \
                else amount

        self.dfPositions.loc[stock, 'PreviousSpot'] = price
        self._tradeHist.append([ctx.date, stock, amount, price])



    def handleEventPre(self):
        pnlDF = self.marginPnL()
        if pnlDF is not None:
            # record position change
            self.dfPositionsHist.append(pnlDF)

            # reset current spot
            ctx = self.context
            self.dfPositions['PreviousSpot'] = pnlDF.set_index('Stock')['Spot']

            # settle daily margin balance
            pnl = pnlDF['PnL'].sum() # HACK Unforunately have to do this before strategy.handleEvent() otherwise would have to implement position effective date in futures Portfolio
            self.logger.info(f'{ctx.date}: futures pnl adjustment: \n{pnlDF}')
            ctx.balance += pnl



class OptionsPortfolio(Portfolio):
    INDEX = ['Stock', 'Strike', 'Maturity', 'PutCall']
    POSITION_COLS = ['Amount']
    PRICING_COLS = ['Spot', 'Strike', 'TimeToMaturity', 'Rate', 'Volatility', 'PutCall', 'Amount']
    GREEKS = ['Price', 'Delta', 'Gamma', 'Theta', 'Vega']
    TRADE_COLS = ['Date'] + INDEX + POSITION_COLS + ['Price']

    def __init__(self, *args, pricer=black_scholes_option_pricer, **kwargs):
        super().__init__(*args, **kwargs)
        self.pricer = pricer
        self.dfExpiryHist = []

        #dynamically create greek functions
        for greek in self.GREEKS:
            setattr(self, greek.lower(), partial(self._getGreek, greek=greek))

    def optionPrice(self, stock: str, strike: float, maturity: date, putcall: int):
        """

        Today's option price for a given Stock, Strike, Maturity, PutCall
        """
        ctx = self.context
        res = self.pricer.price(
            ctx.spot(stock),
            strike,
            (maturity - ctx.date).days / self.pricer.DAYS_IN_YEAR,
            ctx.rate,
            ctx.vol(stock, maturity),
            putcall
        )
        return res

    def todaysMktPrice(self, *args):
        res = self.optionPrice(*args[:4])
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

        putcallstr = OptionTypes(putcall)
        self.logger.info(f'{ctx.date}: trading option: {amount} of {maturity} {strike} {putcallstr} on {stock} @ {price}')
        self._tradeHist.append([ctx.date, stock, strike, maturity, putcallstr, amount, price])

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
        joined['TimeToMaturity'] = (joined['Maturity'] - ctx.date).dt.days / self.pricer.DAYS_IN_YEAR
        joined['Rate'] = ctx.rate

        checkForNulls(joined)
        return joined

    def _pricingParams(self):
        augm = self.dfPositionsAugmented()
        res = augm[self.PRICING_COLS].values.transpose()
        return res

    def positionsGreeks(self):
        paramsDf = self.dfPositionsAugmented()
        for greek in self.GREEKS:
            func = getattr(self.pricer, greek.lower())
            paramsDf[greek] = func(*self._pricingParams())

        self.logger.debug(f'{self.context.date}: greeks: {paramsDf}')
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
            joined['PnL'] = np.where(joined['Amount'] > 0, np.maximum(0, joined['Moniness']), np.minimum(0, joined['Moniness']))
            self.logger.info(f'{ctx.date}: expiring options\n{joined}')
            self.dfExpiryHist.append(joined)

            checkForNulls(joined)

            ctx.balance += joined['PnL'].sum()

            #delete expired options
            self.dfPositions = self.dfPositions.query(f"Maturity > '{maturityStr}'")

    def handleEventPre(self):
        # HACK to clear cached functions for the day
        # for func in (self.positionsGreeks, self.dfPositionsAugmented):
        #     self.logger.debug(f'Memoized: {func.__name__}: {func.cache_info()}')
        #     func.cache_clear()

        if self.context.isTradingDay():
            self.settleOptions()

    def handleEventPost(self):
        self.dfPositionsHist.append(self.positionsGreeks())

