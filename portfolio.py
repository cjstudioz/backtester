import pandas as pd


class Portfolio():
    def __init(self, context):
        self.context = context
        self.options = {}
        self.stock = {}
        self.trades = pd

    def tradeOption(self, object, amount, price):
        self.options.setdefault(object.toTuple(), object).amount += amount
        self.trades.append([str(object), amount, price])

    def expireOptions(self):
