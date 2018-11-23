from backtester.core.option_pricer import OPTION_TYPE_CALL, OPTION_TYPE_PUT
from backtester.core.strategy import Strategy
from backtester.core.context import Context
import pandas as pd

OPTION_TYPES = (OPTION_TYPE_CALL, OPTION_TYPE_PUT)

class StrategyStraddle1(Strategy):
    DEFAULT_STOCKS = ('.SPY',)

    def __init__(self,
                 context: Context,
                 stocks=list(DEFAULT_STOCKS),
                 fractionPerTrade=0.25,
                 maturityBusinessDaysAhead=25,
                 *args, **kwargs):
        self.stocks, self.fractionPerTrade, self.maturityBusinessDaysAhead = stocks, fractionPerTrade, maturityBusinessDaysAhead
        super().__init__(context, *args, **kwargs)



    def handleEvent(self):
        """
        1. Delta hedge optoins position each day
        2. Purchase 25% of cash balance worth of options in stocks list each Friday equally weighted across each stock.
        """
        ctx = self.context

        # Sell 25% options on Friday
        if ctx.date.weekday() == 4:
            refNotional = self.refNotional()
            tradeNotional = (self.refNotional() * self.fractionPerTrade)/len(self.stocks)
            for stock in self.stocks:
                if refNotional >= tradeNotional:
                    maturity = ctx.date + self.maturityBusinessDaysAhead * ctx.businessday
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