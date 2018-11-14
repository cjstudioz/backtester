import numpy as np
import scipy.stats as si
from functools import lru_cache

OPTION_TYPE_CALL = 1
OPTION_TYPE_PUT = -1
DAYS_IN_YEAR = 360

@lru_cache()
def _d1(S, K, T, r, sigma):
    return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

@lru_cache()
def _d2(S, K, T, r, sigma):
    #TODO: derived from d1?
    return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

@lru_cache()
def price(S, K, T, r, sigma, putcall):
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    res = (S * si.norm.cdf(putcall * d1, 0.0, 1.0) - K * np.exp(-r * T) * si.norm.cdf(putcall * d2, 0.0, 1.0))
    return putcall * res

@lru_cache()
def _delta(S, K, T, r, sigma):
    d1 = _d1(S, K, T, r, sigma)
    delta_call = si.norm.cdf(d1, 0.0, 1.0)
    return delta_call

def delta(S, K, T, r, sigma, putcall):
    deltaRaw = _delta(S, K, T, r, sigma)
    if putcall == OPTION_TYPE_PUT:
        deltaRaw -= 1
    return deltaRaw

@lru_cache()
def _prob_density(S, K, T, r, sigma):
    d1 = _d1(S, K, T, r, sigma)
    res = 1 / np.sqrt(2 * np.pi) * np.exp(-d1 ** 2 * 0.5)
    return res

@lru_cache()
def gamma(S, K, T, r, sigma):
    prob_density = _prob_density(S, K, T, r, sigma)
    gamma = prob_density / (S * sigma * np.sqrt(T))
    return gamma

@lru_cache()
def vega(S, K, T, r, sigma):
    prob_density = _prob_density(S, K, T, r, sigma)
    res = S * prob_density * np.sqrt(T)
    return res

@lru_cache()
def theta(S, K, T, r, sigma, putcall):
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    prob_density = _prob_density(S, K, T, r, sigma)
    res = (-sigma * S * prob_density) / (2 * np.sqrt(T)) - putcall * r * K * np.exp(-r * T) * si.norm.cdf(putcall * d2, 0.0, 1.0)
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
        return [self.spot, self.strike, timeToMaturityRaw.days/DAYS_IN_YEAR, self.rate, self.impliedVol, self.optionType]

    def price(self):
        return price(*self._getPricingArgs())

    def delta(self):
        deltaRaw = delta(*self._getPricingArgs())


    def isExpired(self):
        return self.context.date >= self.maturity

if __name__ == '__main__':
    from datetime import date, timedelta

    context = type('test', (object,), {})() #TODO: replace with real context
    context.date = date.today()

    call = Option('SPY', 100, 1, date.today() + timedelta(days=5), 0.01, 0.1, OPTION_TYPE_CALL, context)
    put = Option('SPY', 1, 101, date.today() + timedelta(days=1), 0.01, 0.1, OPTION_TYPE_PUT, context)
    print(call, call.price(), call.delta())
    print(put, put.price(), put.delta())
