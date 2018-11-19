from backtester.core.option_pricer import OPTION_TYPE_CALL, OPTION_TYPE_PUT
from backtester.core.strategy import Strategy
from backtester.core.context import Context
from pandas.tseries.offsets import CustomBusinessDay
#from backtester.core.calendar import getTradingCalendar
import numpy as np


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
        super().__init__(context, *args, **kwargs)


    def handleEvent(self):
        """
        1. Delta hedge optoins position each day
        2. Purchase 25% of cash balance worth of options in stocks list each Friday equally weighted across each stock.
        """
        ctx = self.context
        if ctx.date.weekday() == 4 and np.datetime64(ctx.date) in ctx.tradingdays: #TODO: could be sped up by just iterating through tradingdays but don't want to prematurely optimize
            tradeNotional = -(self.context.balance * self.fractionPerTrade)/len(self.stocks)
            for stock in self.stocks:
                if ctx.balance >= tradeNotional:
                    for putcall in (OPTION_TYPE_CALL, OPTION_TYPE_PUT):
                        self.optionsPortfolio.executeTradeByCash(tradeNotional, stock,
                            ctx.spot(stock),
                            ctx.date + (self.bday * self.maturityBusinessDaysAhead),
                            putcall
                        )
                else:
                    self.logger.warning(f'out of money to trade {tradeNotional}. balance: {ctx.balance}')