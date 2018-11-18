import numpy as np
import scipy.stats as si
from functools import lru_cache

OPTION_TYPE_CALL = 1
OPTION_TYPE_PUT = -1

def _d1(S, K, T, r, sigma):
    return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))


def _d2(S, K, T, r, sigma):
    #TODO: derived from d1?
    return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

def optionPrice(S, K, T, r, sigma, putcall):
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    res = (S * si.norm.cdf(putcall * d1, 0.0, 1.0) - K * np.exp(-r * T) * si.norm.cdf(putcall * d2, 0.0, 1.0))
    return putcall * res

def delta(S, K, T, r, sigma, putcall):
    d1 = _d1(S, K, T, r, sigma)
    res = putcall * si.norm.cdf(putcall * d1, 0.0, 1.0)
    return res

def _prob_density(S, K, T, r, sigma):
    d1 = _d1(S, K, T, r, sigma)
    res = 1 / np.sqrt(2 * np.pi) * np.exp(-d1 ** 2 * 0.5)
    return res

def gamma(S, K, T, r, sigma):
    prob_density = _prob_density(S, K, T, r, sigma)
    gamma = prob_density / (S * sigma * np.sqrt(T))
    return gamma

def vega(S, K, T, r, sigma):
    prob_density = _prob_density(S, K, T, r, sigma)
    res = S * prob_density * np.sqrt(T)
    return res

def theta(S, K, T, r, sigma, putcall):
    d1 = _d1(S, K, T, r, sigma)
    d2 = _d2(S, K, T, r, sigma)
    prob_density = _prob_density(S, K, T, r, sigma)
    res = (-sigma * S * prob_density) / (2 * np.sqrt(T)) - putcall * r * K * np.exp(-r * T) * si.norm.cdf(putcall * d2, 0.0, 1.0)
    return res
