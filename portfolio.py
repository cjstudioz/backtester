import pandas as pd


class Portfolio:
    def __init(self, context):
        self.context = context
        self.options = {}
        self.stock = {}
        self.trades = pd

    def tradeOption(self, object, amount, price):
        self.options.setdefault(object.toTuple(), object).amount += amount
        self.trades.append([str(object), amount, price])

    def settleOptions(self):
        settlement = 0
        expiredOptions = [v for v in self.options.values() if v.isExpired()]

        if expiredOptions:
            settlement = sum(option.moniness for option in expiredOptions)
            self.options = {k: v for k, v in self.options.iteritems() if not v.isExpired()}

        return settlement