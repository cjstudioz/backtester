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
    def __init__(self, underlying, strike, maturity, optionType, amount, context):
        if optionType not in (OPTION_TYPE_CALL, OPTION_TYPE_PUT):
            raise RuntimeError('invalid option type: %s. use either 0 for call or 1 for put' % optionType)
        self.underlying, self.strike, self.maturity, self.optionType, self.amount, self.context = \
            underlying, strike, maturity, optionType, amount, context

        self.putcallsign = self.optionType #simplifies code but hacky I know not sure how I feel about it

    def __str__(self):
        return 'Option%s' % vars(self)

    def _getPricingArgs(self):
        if self.isExpired():
            raise RuntimeError('Option is expired! marutity:{}, context.date:{}'.format(self.maturity, self.context.date))

        timeToMaturityRaw = self.maturity - self.context.date
        return [
            self.context.spot(self.underlier),
            self.strike,
            timeToMaturityRaw.days/DAYS_IN_YEAR,
            self.context.rate,
            self.context.spot(self.underlier),
            self.putcallsign
        ]

    def price(self):
        return self.amount * price(*self._getPricingArgs())

    def delta(self):
        return self.amount * delta(*self._getPricingArgs())

    def settle(self):
        if context.date < self.maturity: #TODO: should this be stricter? would need to record spot on maturity
            raise RuntimeError('Can only settle after maturity context.date:%s, maturity: %s' % (context.date, self.maturity))

        moniness = self.amount * self.putcallsign * (context.spot(self.underlying) - self.strike)
        res = max(0, moniness) if self.amount > 0 else min(0, moniness)


    def isExpired(self):
        return self.context.date >= self.maturity

if __name__ == '__main__':
    from datetime import date, timedelta

    context = type('test', (object,), {})() #TODO: replace with real context
    context.date = date.today()

    call = Option('SPY', 100, 1, date.today() + timedelta(days=5), 0.01, 0.1, OPTION_TYPE_CALL, 2, context)
    put = Option('SPY', 1, 101, date.today() + timedelta(days=1), 0.01, 0.1, OPTION_TYPE_PUT, 3.5, context)
    print(call, call.price(), call.delta())
    print(put, put.price(), put.delta())

    options = [
        Option('SPY', 100, 90, date.today(), 0.01, 0.1, OPTION_TYPE_CALL, 1, context),
        Option('SPY', 100, 110, date.today(), 0.01, 0.1, OPTION_TYPE_CALL, 2, context),
        Option('SPY', 100, 100, date.today(), 0.01, 0.1, OPTION_TYPE_CALL, 3.6, context),
        Option('SPY', 100, 90, date.today(), 0.01, 0.1, OPTION_TYPE_PUT, 1, context),
        Option('SPY', 100, 110, date.today(), 0.01, 0.1, OPTION_TYPE_PUT, 2.5, context),
        Option('SPY', 100, 100, date.today(), 0.01, 0.1, OPTION_TYPE_PUT, 50, context),
    ]
    for op in options:
        print(op, op.settle())
