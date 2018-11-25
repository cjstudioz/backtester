import re
import requests

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
    response = requests.post(url, data=data, headers={'Content-type': 'application/x-www-form-urlencoded'})
    res = {metric: float(re.search(f'{metric}</A></B> =\s+(-*\d+\.*\d*)(,| )', str(response.content)).groups()[0])
           for metric in ['Value', 'Delta', 'Gamma', 'Theta']}
    return res
