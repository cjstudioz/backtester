# import sys
# sys.path.append(r'C:\Users\Administrator\PycharmProjects\backtester')

import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

from backtester.core.context import Context
from backtester.strategies.straddle1 import StrategyStraddle1
from backtester.utils.mktdata import getSampleMktData
from datetime import datetime


if __name__ == '__main__':
    dfMktdata = getSampleMktData()
    context = Context(dfMktdata,
                      balance=1000,
                      #enddate=datetime(2013, 5, 5)
    )
    
    strategy = StrategyStraddle1(context)
    strategy.run()
        
    
    # Reporting out CSVs which is eventually consumed by Tableau
    import pandas as pd
    
    primarykey = ['Date','Stock']
    dfPositionsHistOptions = pd.concat(strategy.optionsPortfolio.dfPositionsHist)
    dfGreeksAgg = dfPositionsHistOptions.groupby(primarykey)[strategy.optionsPortfolio.GREEKS].sum().reset_index()
    dfPositionsHistFutures = pd.concat(strategy.stockPortfolio.dfPositionsHist)
    dfNotional = strategy.dfNotionalHist()
    dfExpiryHist = pd.concat(strategy.optionsPortfolio.dfExpiryHist)    
    
    dfTradeHistOptions = strategy.optionsPortfolio.dfTradeHist()
    dfTradeHistOptions['PnL'] = dfTradeHistOptions.eval('-Price * Amount')    
    dfTradeHistOptionsAggPnL = pd.concat([
            dfTradeHistOptions[primarykey + ['PnL']],
            dfExpiryHist[primarykey + ['PnL']]
    ]).groupby(primarykey).sum().reset_index()
    
    dfTradeHistStock = strategy.stockPortfolio.dfTradeHist()
        
    
    csvOutputDir = 'c:/temp/strategy_results2/'
    localItems = {k: v for k,v in locals().items() if k.startswith('df')}
    for attr, val in localItems.items():    
        print(f'writing {attr}')
        val.to_csv(csvOutputDir  + attr + '.csv', index=False)
                