from backtester.core.portfolio import OptionsPortfolio, FuturesPortfolio
from backtester.core.context import Context
import logging
import pandas as pd

class Strategy:
    """
    Base class for all other strategies to inherit from. just implement the handleEvent() method in the subclass
    """
    def __init__(self, context: Context, processWeekendsHols= False):
        self.context, self.processWeekendsHols = context, processWeekendsHols
        self.optionsPortfolio = OptionsPortfolio(context)
        self.stockPortfolio = FuturesPortfolio(context)
        self._notionalHist = []
        self.logger = logging.getLogger(__name__)

    def run(self):
        while self.context.nextEvent():
            if self.processWeekendsHols or self.context.isTradingDay(): # TODO: could be sped up by just iterating through tradingdays but don't want to prematurely optimize
                self.optionsPortfolio.handleEventPre()
                self.stockPortfolio.handleEventPre()
                self.handleEvent()
                self.stockPortfolio.handleEventPost()
                self.optionsPortfolio.handleEventPost()
                self.handleReporting()

    def refNotional(self):
        """

        Current Total Value of all portfolios including cash
        TODO: unsure if this belongs in context instead
        """
        res = self.context.balance + self.optionsPortfolio.notional() #+ self.stockPortfolio.notional()
        return res

    def handleReporting(self):
        ctx = self.context
        optionsNotional = self.optionsPortfolio.notional()
        refNotional = self.refNotional()
        self.logger.info(
            f'{ctx.date}: eod Balance: {ctx.balance}, Options: {optionsNotional}, Stock: {self.stockPortfolio.notional()}, ref_notional: {refNotional}')
        self._notionalHist.append([ctx.date, ctx.balance, optionsNotional, refNotional])

    def dfNotionalHist(self):
        """
        For Post Sim Reporting build a dataframe trade history list
        """
        res = pd.DataFrame(self._notionalHist, columns=['Date', 'CashBalance', 'OptionsPosition', 'RefNotional'])
        return res

    def handleEvent(self):
        raise NotImplementedError()


