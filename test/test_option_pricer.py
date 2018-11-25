import unittest
import pandas as pd
import numpy as np
from backtester.pricers import black_scholes_option_pricer as bsp
from backtester.pricers.option_types import OptionTypes
from test.web_options_pricer import webOptionsPricerWrapper
from multiprocessing.pool import ThreadPool
import logging
logger = logging.getLogger(__name__)

pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 20)

class TestVanillaEuPricer(unittest.TestCase):
    """
    HACK: This isn't meant ot be a unit test but rather a one off sanity test using random numbers into another model
    I'm aware unit tests should be reproducable and ideally self contained.
    Could potentially persist the random inputs and external results and test against that
    """
    POOL = ThreadPool(8)

    def _generateInputs(self, size=100):
        randomArray = np.random.rand(6, size)
        randomArray[0] *= 100 #spot
        randomArray[1] = np.random.lognormal(0, 0.5, size) * randomArray[0]
        randomArray[2] *= 5 #time to maturity
        randomArray[3] /= 5 #rates
        randomArray[4] *= 4 #rates
        randomArray[5] = 1
        return randomArray


    def test_sample(self, epsilon = 1e-04):
        inputs = self._generateInputs()
        greeks = ['price', 'delta', 'gamma', 'theta']
        bulkRes = {}
        errorCount = 0

        for putcall in OptionTypes:
            inputs[5] = putcall.value
            webinputs = inputs.transpose()

            bulkRes.setdefault('inputs', {})[putcall.name] = pd.DataFrame(webinputs)

            bulkRes.setdefault('numpy', {})[putcall.name] = pd.DataFrame(
                {greek: getattr(bsp, greek)(*inputs) for greek in greeks}
            )

            bulkRes.setdefault('py', {})[putcall.name] = pd.DataFrame(
                {greek: [getattr(bsp, greek)(*webinput) for webinput in webinputs] for greek in greeks}
            )

            bulkRes.setdefault('web', {})[putcall.name] = pd.DataFrame(
                self.POOL.map(lambda webinput: webOptionsPricerWrapper(*webinput), webinputs)
            )

        for restype in ['py', 'numpy']:
            # restype = 'py'
            # deltas sum to 1
            sumdelta = bulkRes[restype]['CALL']['delta'] - bulkRes[restype]['PUT']['delta']
            mask = sumdelta != 1
            self.assertTrue(sumdelta[mask].empty, 'put + call delta == 1')

            for putcall in OptionTypes:
                # putcall = OptionTypes.PUT
                bulkRes[restype][putcall.name]['theta'] /= 365 #HACK since web result returns annual theta instead of daily
                epsilons = bulkRes[restype][putcall.name] - bulkRes['web'][putcall.name]
                mask = (epsilons.abs() > epsilon).any(axis=1)

                if not epsilons[mask].empty:
                    diffs = pd.concat([
                        bulkRes['inputs'][putcall.name][mask],
                        epsilons[mask],
                        bulkRes[restype][putcall.name][mask],
                        bulkRes['web'][putcall.name][mask],
                    ], axis=1)
                    logger.error(f'unexpected diff for {restype},{putcall}:\n{diffs}')
                    errorCount += 1

        self.assertFalse(errorCount > 0, f'found {errorCount} errors see log above for detail, or put debug in diffs variable')

if __name__ == '__main__':
    unittest.main()

