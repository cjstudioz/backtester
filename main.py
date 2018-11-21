from backtester.core.context import Context
from backtester.strategies.straddle1 import StrategyStraddle1
from backtester.utils.mktdata import createVolSurface

if __name__ == '__main__':
    filaname = r'C:\Users\Administrator\PycharmProjects\backtester\data\spx_vols.txt'
    mktdata = createVolSurface(filaname)
    context = Context(mktdata, balance=10000)

    strategy = StrategyStraddle1(context)
    strategy.run()

    #post process
    df1 = pd.concat(strategy.optionsPortfolio.dfPositionsHist)
    df2 = pd.concat(strategy.stockPortfolio.dfPositionsHist)
    df = pd.merge(df1, df2, how='outer', on=['Date'])
    from IPython.display import display, HTML

    display(HTML(df.to_html()))