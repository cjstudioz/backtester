#Vanila Options BackTester:

## Quick Start
Open example jupyter notebook online here:
https://mybinder.org/v2/gh/cjstudioz/backtester/master?filepath=example.ipynb

##Sample Results
https://public.tableau.com/profile/some.guy2184#!/vizhome/Book2_24238/Dashboard1

## limitations and assumptions
- CFD requires no margin and can trade position even when no balance
- Futures Pnl settled before reference Notional Calculated (HACK)
- Only supports european options at the moment
= Able to trade fractional lots to achieve exact % of reference notional. and perfectly hedge
- Very little attention has been given to floating point precision. 