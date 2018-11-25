
from backtester.core.context import Context
from backtester.strategies.straddle1 import StrategyStraddle1
from backtester.utils.mktdata import getSampleMktData
from datetime import datetime, timedelta
import unittest
import math

import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

class TestStrategy(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup()

    def _setup(self):
        dfMktdata = getSampleMktData()
        self.context = Context(dfMktdata,
            balance=1000,
            rate=0.02,
            enddate=dfMktdata['Date'].min() + timedelta(days=17)
        )

    def test_short_strategy(self):
        strategy = StrategyStraddle1(self.context,
            maturityBusinessDaysAhead=3,
        )
        strategy.run()
        finalNotional = strategy.refNotional()
        expectedNotional = 1168.451777
        self.assertTrue(math.isclose(finalNotional, expectedNotional), f'expected Notional: {expectedNotional} actual: {finalNotional}')

    def test_long_strategy(self):
        strategy = StrategyStraddle1(self.context,
            # stocks = list(DEFAULT_STOCKS),
            fractionPerTrade=0.4,
            maturityBusinessDaysAhead=2,
        )
        strategy.run()
        finalNotional = strategy.refNotional()
        expectedNotional = 1757.09797
        self.assertTrue(math.isclose(finalNotional, expectedNotional), f'expected Notional: {expectedNotional} actual: {finalNotional}')