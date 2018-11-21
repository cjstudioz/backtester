from backtester.core.option_pricer import OPTION_TYPE_CALL, OPTION_TYPE_PUT
from backtester.core.strategy import Strategy
from backtester.core.context import Context
from pandas.tseries.offsets import CustomBusinessDay
#from backtester.core.calendar import getTradingCalendar
import numpy as np

OPTION_TYPES = (OPTION_TYPE_CALL, OPTION_TYPE_PUT)

class StrategyStraddle1(Strategy):
    DEFAULT_STOCKS = ('.SPY',)

    def __init__(self,
                 context: Context,
                 stocks=list(DEFAULT_STOCKS),
                 fractionPerTrade=0.25,
                 maturityBusinessDaysAhead=25,
                 businessDay=None,
                 *args, **kwargs):
        self.stocks, self.fractionPerTrade, self.maturityBusinessDaysAhead = stocks, fractionPerTrade, maturityBusinessDaysAhead
        self.bday = businessDay or CustomBusinessDay(calendar=context.mktdata['Date'].unique())
        self.notionalDf = []
        super().__init__(context, *args, **kwargs)


    def handleEvent(self):
        """
        1. Delta hedge optoins position each day
        2. Purchase 25% of cash balance worth of options in stocks list each Friday equally weighted across each stock.
        """

        ctx = self.context
        if ctx.isTradingDay(): #Only process business days. TODO: could be sped up by just iterating through tradingdays but don't want to prematurely optimize
            refNotional = self.refNotional()
            optionsNotional = self.optionsPortfolio.notional()
            self.logger.info(f'{ctx.date}: Balance: {ctx.balance}, Options: {self.optionsPortfolio.notional()}, Stock: {self.stockPortfolio.notional()}, ref_notional: {refNotional}')
            self.notionalDf.append([ctx.date, ctx.balance, optionsNotional])

            # Sell 25% options on Friday
            if ctx.date.weekday() == 4:
                tradeNotional = (self.refNotional() * self.fractionPerTrade)/len(self.stocks)
                for stock in self.stocks:
                    if refNotional >= tradeNotional:
                        maturity = ctx.date + (self.maturityBusinessDaysAhead * self.bday)
                        straddleprice = sum([ctx.optionPrice(stock, ctx.spot(stock), maturity, putcall) for putcall in OPTION_TYPES])
                        amount = tradeNotional/straddleprice/2
                        for putcall in OPTION_TYPES:
                            self.optionsPortfolio.executeTrade(-amount, stock, ctx.spot(stock), maturity, putcall)
                    else:
                        #raise RuntimeError(f'{ctx.date}: out of money to trade {tradeNotional}. balance: {ctx.balance}')
                        self.logger.warning(f'{ctx.date}: out of money to trade {tradeNotional}. balance: {ctx.balance}')

            # Delta Hedge
            deltaByStockDF = self.optionsPortfolio.delta()
            for stock, deltaAmt in deltaByStockDF.iteritems():
                self.stockPortfolio.executeTradeTargetAmount(deltaAmt, stock)