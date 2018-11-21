import numpy as np
import scipy.stats as si
from functools import lru_cache

OPTION_TYPE_CALL = 1
OPTION_TYPE_PUT = -1

def _d1(S, K, T, r, sigma):
    return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))


def _d2(S, K, T, r, sigma):
    #TODO: derived from d1?
    return (np.log(S / K) + (r - 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

def price(S, K, T, r, sigma, putcall, amount=1):
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    res = (S * si.norm.cdf(putcall * d1, 0.0, 1.0) - K * np.exp(-r * T) * si.norm.cdf(putcall * d2, 0.0, 1.0))
    return amount * putcall * res

def delta(S, K, T, r, sigma, putcall, amount=1):
    d1 = _d1(S, K, T, r, sigma)
    res = putcall * si.norm.cdf(putcall * d1, 0.0, 1.0)
    return res * amount

def _prob_density(S, K, T, r, sigma):
    d1 = _d1(S, K, T, r, sigma)
    res = 1 / np.sqrt(2 * np.pi) * np.exp(-d1 ** 2 * 0.5)
    return res

def gamma(S, K, T, r, sigma, _putcall_unused, amount=1):
    #TODO: not sure how I feel about putting an unused arg just to fit the general func signature
    prob_density = _prob_density(S, K, T, r, sigma)
    res = prob_density / (S * sigma * np.sqrt(T))
    return res * amount

def vega(S, K, T, r, sigma, _putcall_unused, amount=1):
    #TODO: not sure how I feel about putting an unused arg just to fit the general func signature
    prob_density = _prob_density(S, K, T, r, sigma)
    res = S * prob_density * np.sqrt(T)
    return res * amount

def theta(S, K, T, r, sigma, putcall, amount=1):
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    prob_density = _prob_density(S, K, T, r, sigma)
    res = (-sigma * S * prob_density) / (2 * np.sqrt(T)) - putcall * r * K * np.exp(-r * T) * si.norm.cdf(putcall * d2, 0.0, 1.0)
    return res * amount

if __name__ == '__main__':
    print(optionPrice(50, 50, 1, 0.05, 0.25, 1))
    print(optionPrice(50, 50, 1, 0.05,
    0.25,
    -1))