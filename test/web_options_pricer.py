import re
import requests
import logging
logger = logging.getLogger(__name__)
WEB_OPTION_PRICER_URL = 'http://www.intrepid.com/robertl/option-pricer1/option-pricer.cgi'


def webOptionsPricer(
        price,
        strike,
        yield_,  # bad choice of names
        rate,
        volatility,
        tenor,
        type=0,  # 0 call, 1 put
        count=2,  # 0 day, 1 month 2 year
        form=1,  # 0 American, 0 European
):
    data = dict(locals(), **{'yield': yield_})
    response = requests.post(WEB_OPTION_PRICER_URL, data=data, headers={'Content-type': 'application/x-www-form-urlencoded'})
    res = {metric: float(re.search(f'{metric}</A></B> =\s+(-*\d+\.*\d*)(\,| )', str(response.content)).groups()[0])
           for metric in ['Value', 'Delta', 'Gamma', 'Theta']}
    return res

def webOptionsPricerWrapper(
    price,
    strike,
    tenor,
    rate,
    volatility,
    type,
):
    newType = 0 if type == 1 else 1
    logger.debug('seding remote request')
    res =  webOptionsPricer(
        price,
        strike,
        0,
        rate*100,
        volatility*100,
        tenor,
        newType  # 0 call, 1 put
    )
    return {('price' if k == 'Value' else k.lower()): v for k,v in res.items()}