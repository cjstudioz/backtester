from backtester.core.portfolio import OptionsPortfolio, FuturesPortfolio
from backtester.core.context import Context
import logging

class Strategy:
    def __init__(self, context: Context):
        self.context = context
        self.optionsPortfolio = OptionsPortfolio(context)
        self.stockPortfolio = FuturesPortfolio(context)
        self.logger = logging.getLogger(__name__)

    def run(self):
        while self.context.nextEvent():
            self.optionsPortfolio.handleEventPre()
            self.stockPortfolio.handleEventPre()
            self.handleEvent() #NOTE this has to come last after all other market admin handlers done. TODO: may extend other handlers to have pre and post strategy handlers
            #self.logger.debug(f'{self.context.date}: balance: {self.refNotional()}')
            self.optionsPortfolio.handleEventPost()
            self.stockPortfolio.handleEventPost()

    def refNotional(self):
        """

        Current Total Value of all portfolios including cash
        TODO: unsure if this belongs in context instead
        """
        res = self.context.balance + self.optionsPortfolio.notional() #+ self.stockPortfolio.notional()
        return res

    def handleEvent(self):
        raise NotImplementedError()


