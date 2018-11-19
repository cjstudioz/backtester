from backtester.core.portfolio import OptionsPortfolio
from backtester.core.context import Context
import logging

class Strategy:
    def __init__(self, context: Context):
        self.context = context
        self.optionsPortfolio = OptionsPortfolio(context)
        self.logger = logging.getLogger(__name__)

    def run(self):
        while self.context.nextEvent():
            self.handleEvent()
            self.optionsPortfolio.handleEvent()
            self.logger.debug(f'balance: {self.context.balance}')

    def handleEvent(self):
        raise NotImplementedError()


