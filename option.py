import numpy as np
import scipy.stats as si
from functools import lru_cache

OPTION_TYPE_CALL = 1
OPTION_TYPE_PUT = 0
DAYS_IN_YEAR = 360

@lru_cache()
def _d1(S, K, T, r, sigma):
    return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

@lru_cache()
def _d2(S, K, T, r, sigma):
    #TODO: derived from d1?
    return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

@lru_cache()
def callPrice(S, K, T, r, sigma):
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    res = (S * si.norm.cdf(d1, 0.0, 1.0) - K * np.exp(-r * T) * si.norm.cdf(d2, 0.0, 1.0))
    return res

@lru_cache()
def putPrice(S, K, T, r, sigma):
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    res = (K * np.exp(-r * T) * si.norm.cdf(-d2, 0.0, 1.0) - S * si.norm.cdf(-d1, 0.0, 1.0))
    return res



class Option():
    def __init__(self, underlying, spot, strike, maturity, rate, impliedVol, optionType, context):
        if optionType not in (OPTION_TYPE_CALL, OPTION_TYPE_PUT):
            raise RuntimeError('invalid option type: %s. use either 0 for call or 1 for put' % optionType)
        self.underlying, self.spot, self.strike, self.maturity, self.rate, self.impliedVol, self.optionType, self.context = \
            underlying, spot, strike, maturity, rate, impliedVol, optionType, context

    def __str__(self):
        return 'Option%s' % vars(self)

    def _getPricingArgs(self):
        if self.isExpired():
            raise RuntimeError('Option is expired! marutity:{}, context.date:{}'.format(self.maturity, self.context.date))

        timeToMaturityRaw = self.maturity - self.context.date
        return [self.spot, self.strike, timeToMaturityRaw.days/DAYS_IN_YEAR, self.rate, self.impliedVol]

    def price(self):
        args = self._getPricingArgs()
        res = callPrice(*args) if self.optionType == OPTION_TYPE_CALL else putPrice(*args)
        return res

    def isExpired(self):
        return self.context.date >= self.maturity

if __name__ == '__main__':
    from datetime import date, timedelta

    context = type('test', (object,), {})() #TODO: replace with real context
    context.date = date.today()
    call = Option('SPY', 100, 101, date.today() + timedelta(days=5), 0.01, 0.1, OPTION_TYPE_CALL, context)
    put = Option('SPY', 100, 101, date.today() + timedelta(days=5), 0.01, 0.1, OPTION_TYPE_PUT, context)
    print(call, call.price())
    print(put, put.price())
