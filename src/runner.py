import DailyStockData as stocks
import ABANDS
import ADX
import KAMA 
import BackTesting
import COVIDReverseThrottleGap
import json
import pandas as pd
import numpy as np



allTickers = pd.read_csv('../data/trackedTickers.csv')

allData = []

def backTestCRTG(ticker):
    try:
        x = stocks.getDailyPrice(ticker)

        CRTG = COVIDReverseThrottleGap.getBackTestDF(x)

        currentTotal = BackTesting.backTestLimits(CRTG, .05, -.03)

        print('successfully retreived data for ' + ticker)

        return currentTotal

    except:

        print('unable to run algo on: ' + ticker)

        return 0


bt = np.vectorize(backTestCRTG)

allTickers = allTickers.head(10)

allTickers['CRTG_Strat'] = bt(allTickers.ticker)

allTickers.to_csv('../data/CRTG.csv')



#x = BackTesting.getOptimalSignals(x)

#data = KAMA.optimizeParameters(x)

#with open('SNAPKAMA.json', 'w') as f:
#    json.dump(data, f)



