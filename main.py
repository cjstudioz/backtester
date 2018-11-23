# import sys
# sys.path.append(r'C:\Users\Administrator\PycharmProjects\backtester')

import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

from backtester.core.context import Context
from backtester.strategies.straddle1 import StrategyStraddle1
from backtester.utils.mktdata import createVolSurface
from datetime import datetime

if __name__ == '__main__':
    filaname = r'C:\Users\Administrator\PycharmProjects\backtester\data\spx_vols.txt'
    dfMktdata = createVolSurface(filaname)
    context = Context(dfMktdata,
                      balance=10000,
                      #enddate=datetime(2013, 5, 5)
    )
    
    strategy = StrategyStraddle1(context)
    strategy.run()
        
    # Reporting out CSVs
    import pandas as pd
    
    dfPositionsHistOptions = pd.concat(strategy.optionsPortfolio.dfPositionsHist)
    dfGreeksAgg = dfPositionsHistOptions.groupby(['Date','Stock'])[strategy.optionsPortfolio.GREEKS].sum().reset_index()
    dfPositionsHistFutures = pd.concat(strategy.stockPortfolio.dfPositionsHist)
    dfNotional = strategy.dfNotionalHist()
    dfExpiryHist = pd.concat(strategy.optionsPortfolio.dfExpiryHist)
    dfTradeHistOptions = strategy.optionsPortfolio.dfTradeHist()
    dfTradeHistStock = strategy.stockPortfolio.dfTradeHist()
    
    
    csvOutputDir = 'c:/temp/strategy_results/'
    localItems = {k: v for k,v in locals().items() if k.startswith('df')}
    for attr, val in localItems.items():    
        print(f'writing {attr}')
        val.to_csv(csvOutputDir  + attr + '.csv', index=False)
                