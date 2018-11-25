from  numpy import exp, log, sqrt
from scipy.stats import norm

DAYS_IN_YEAR = 360

def _d1(S, K, T, r, sigma):
    return (log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))


def _d2(S, K, T, r, sigma):
    #TODO: derived from d1?
    return (log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))

def price(S, K, T, r, sigma, putcall, amount=1):
    """

    option price

    :param S: Spot
    :param K:  Strike
    :param T: time to maturity in years #TODO: change func signatures to take T in days instead of years
    :param r: interest rate 0.01 = 1%/annum
    :param sigma: implied vol / annum
    :param putcall: 1 call, -1 put see backtester.pricer.option_types
    :param amount: optional position quantity multiplier
    :return:
    """
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    res = (S * norm.cdf(putcall * d1, 0.0, 1.0) - K * exp(-r * T) * norm.cdf(putcall * d2, 0.0, 1.0))
    return amount * putcall * res

def delta(S, K, T, r, sigma, putcall, amount=1):
    d1 = _d1(S, K, T, r, sigma)
    res = putcall * norm.cdf(putcall * d1, 0.0, 1.0)
    return res * amount

def gamma(S, K, T, r, sigma, _putcall_unused, amount=1):
    #TODO: not sure how I feel about putting an unused arg just to fit the general func signature
    d1 = _d1(S, K, T, r, sigma)    
    res = norm.pdf(d1) / (S * sigma * sqrt(T))
    return res * amount

def vega(S, K, T, r, sigma, _putcall_unused, amount=1):
    #TODO: not sure how I feel about putting an unused arg just to fit the general func signature
    d1 = _d1(S, K, T, r, sigma)    
    res = S * norm.pdf(d1) * sqrt(T)
    return res * amount

def theta(S, K, T, r, sigma, putcall, amount=1):
    """
    :return: Theta per day (instead of year)
    """
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)    
    res = (-sigma * S * norm.pdf(d1)) / (2 * sqrt(T)) - putcall * r * K * exp(-r * T) * norm.cdf(putcall * d2)
    return res * amount

