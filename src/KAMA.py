import pandas as pd
import numpy as np

def getEfficiencyRatio(priceDF, windowSize):
    KAMADF = pd.DataFrame()

    KAMADF['change'] = priceDF.Close.rolling(windowSize).agg(lambda rows: rows[-1] - rows[0])

    KAMADF['volatility'] = priceDF.Close.rolling(2).agg(lambda rows: abs(rows[-1] - rows[0]))
    KAMADF.volatility = KAMADF.volatility.fillna(0)
    KAMADF.volatility = KAMADF.volatility.rolling(windowSize).sum()

    KAMADF['EfficiencyRatio'] = KAMADF.change / KAMADF.volatility

    KAMADF = KAMADF.drop(columns=['change','volatility'])

    return KAMADF

# Kaufman Adaptive Moving Average
# calc efficiency ratio
# smooth efficiency ratio with EMA Smoothing constant
# calc KAMA with: Current KAMA = Prior KAMA + SC x (Price - Prior KAMA)
def getDF(priceDF, windowSize=10, fastestSC=2, slowestSC=30):

    KAMADF = getEfficiencyRatio(priceDF, windowSize)
   
    KAMADF['SmoothingConstant'] = (KAMADF.EfficiencyRatio * (2/(2+1) - 2/(30+1)) + 2/(30+1))**2

    KAMADF['Price'] = priceDF.Close
    KAMADF = KAMADF.dropna()

    finalKAMA = []
    priorKAMA = KAMADF.Price[0]

    for index, row in KAMADF.iterrows():
        priorKAMA = priorKAMA + row.SmoothingConstant * (row.Price - priorKAMA)
        finalKAMA.append(priorKAMA)
        
    KAMADF['KAMA'] = finalKAMA
    priceDF['KAMA'] = KAMADF.KAMA
    KAMADF = None

    return priceDF

def scan(priceDF, windowSize=10, shortRangeFastestSC=2, longRangeFastestSC=5, shortRangeSlowestSC=30, longRangeSlowestSC=30):

    volSMA = priceDF.Volume[-20:].mean() > 100000

    if volSMA:
        longRangeKAMA = (getDF(priceDF,windowSize,longRangeFastestSC,longRangeSlowestSC))['KAMA']
        longRangeKAMAMean = (longRangeKAMA[-50:]).mean()
        shortRangeKAMA = getDF(priceDF,windowSize,shortRangeFastestSC,shortRangeSlowestSC)['KAMA']

        if longRangeKAMA[-1] > longRangeKAMAMean:
            if priceDF.Close[-1] > shortRangeKAMA[-1]:
                return 1
        elif longRangeKAMA[-1] < longRangeKAMAMean:
            if priceDF.Close[-1] < shortRangeKAMA[-1]:
                return -1
        else:
            return 0
    else:
        return 0

def getBackTestDF(priceDF, windowSize=10, shortRangeFastestSC=2, longRangeFastestSC=5, shortRangeSlowestSC=30, longRangeSlowestSC=30, optimizeOnly=False):
    signals = list(np.zeros(windowSize))
    priceDF['idx'] = np.arange(len(priceDF))

    for index in range(windowSize,len(priceDF)):
        signals.append(scan(priceDF.loc[priceDF.idx < index], windowSize, shortRangeFastestSC, longRangeFastestSC, shortRangeSlowestSC, longRangeSlowestSC))
        
    print(len(signals))
    print(len(priceDF))

    priceDF['signals'] = signals
    priceDF.signals = priceDF.fillna(0)

    if optimizeOnly:
        return priceDF.signals
    else:
        return priceDF

def getOptimizedParameters(priceDFwOptimizedSignals):
    
    currentBest = None
    optimalParameters = {'windowSize':10,'shortRangeFastestSC':2,'shortRangeSlowestSC':30,'longRangeFastestSC':5,'longRangeSlowestSC':30}

    for windowSize in range(5,15): #x10
        for shortRangeFastestSC in range(2,7): #x40
            for dist in range(1,5):             #x160
                longRangeFastestSC = shortRangeFastestSC + dist
                optimized = getBackTestDF(priceDFwOptimizedSignals, windowSize, shortRangeFastestSC, longRangeFastestSC, 30, 30, True)
                score = abs((priceDFwOptimizedSignals.optimalSignals - optimized).sum())

                if currentBest == None:
                    currentBest = score
                elif currentBest > score:
                    print(currentBest)
                    currentBest = score
                    print(currentBest)
                    optimalParameters['windowSize'] = windowSize
                    optimalParameters['shortRangeFastestSC'] = shortRangeFastestSC
                    optimalParameters['shortRangeSlowestSC'] = 30
                    optimalParameters['longRangeFastestSC'] = longRangeFastestSC
                    optimalParameters['longRangeSlowestSC'] = 30
    return {'KAMA': optimalParameters}




