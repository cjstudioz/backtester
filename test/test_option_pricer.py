import unittest
from test.web_options_pricer import webOptionsPricer
from backtester.core

class TestVanillaEuPricer(unittest.TestCase):
    def test_sample(self):
        webOptionsPricer(50.0000, 100.0000, 0.00, 5.00, 25.00, 1.0000)

if __name__ == '__main__':
    unittest.main()



class TestVanillaEuPricer()





for _ in range(100):
    params = [
        randint(0, 200),
        randint(0, 200),
        0,
        randint(0, 100) / 10,
        randint(0, 100),
        randint(0, 100) / 100,
    ]
    put, call = [webOptionsPricer(*params + [putcall]) for putcall in (0, 1)]
    print(put, call)