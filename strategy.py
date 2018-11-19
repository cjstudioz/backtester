from portfolio import OptionsPortfolio
from context import Context

class Strategy:
    def __init__(self, context: Context):
        self.context = context
        self.optionsPortfolio = OptionsPortfolio(context)

    def run(self):
        while self.context.nextEvent():
            self.handleEvents()

    def parseEvent(self):
        raise NotImplementedError()


