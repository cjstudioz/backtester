import pandas as pd

class Portfolio():
    def __init(self, context):
        self.context = context
        self.options = {}
        self.stock = {}
        self.trades = pd

    def tradeOption(self, option: tuple, underlying: str, price: double, amount: double):
        self.options.setdefault(
            underlying, {}
        ).setdefault(option, 0) += amount

        self.options.QUERY

        #self.trades.append(*(option + (underlying, price, amount)))

    def delta(underlying):
        ctx = self.context
        sum(delta(
            ctx.spot(underlying),
            option.strike,
            (option.maturity - ctx.date).days / ctx.DAYS_IN_YEAR,
            ctx.rate,
            ctx.vol(underlying)
        ) for option in self.options[underlying].values())

    def settleOptions(self):
        settlement = 0
        expiredOptions = [v for v in self.options.values() if v.isExpired()]

        if expiredOptions:
            settlement = sum(option.moniness for option in expiredOptions)
            self.options = {k: v for k, v in self.options.iteritems() if not v.isExpired()}

        return settlement