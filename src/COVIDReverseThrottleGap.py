from utilities import getPercChange
import numpy as np
import pandas as pd

def marketValueComparison(priceDF, compareDate):
    percChange = getPercChange(priceDF.Close.iloc[-1] , priceDF.Close[compareDate])
    return percChange

def scan(priceDF, windowSize=100, recencyWindow=22, maxToLocalMaxDiff=-.03, recentMaxToCurrentDiff=-.06, currentPriceToMinDiff=.03, COVID=False):
    windowDF = priceDF.tail(windowSize)
    minPrice = windowDF.Close.min()
    maxPrice = windowDF.Close.max()
    currentPrice = windowDF.tail(1).Close.values
    # if price is close to low than high
    if abs(getPercChange(currentPrice, maxPrice)) > abs(getPercChange(currentPrice, minPrice)):    
        recentMax = windowDF.tail(recencyWindow).Close.max()
        # if recent max is lower than the max
        if getPercChange(recentMax, maxPrice) < -.03:
            # if recent max is higher than current price by 6% 
            if getPercChange(currentPrice, recentMax) < (-.06):
                # if current price is higher than min by 3%
                if getPercChange(currentPrice, minPrice) > .03:
                    if not COVID:
                        return 1
                    elif marketValueComparison(priceDF, pd.Timestamp('2020-02-19')) > -.078 and COVID:
                        return 1
                    
    return 0

def getBackTestDF(priceDF, windowSize=100, recencyWindow=22, maxToLocalMaxDiff=-.03, recentMaxToCurrentDiff=-.06, currentPriceToMinDiff=.03, optimizeOnly=False):
    signals = list(np.zeros(windowSize))
    priceDF['idx'] = np.arange(len(priceDF))

    COVID = False
    for index in range(windowSize,len(priceDF)):
        if COVID == False and priceDF.loc[priceDF.idx == index].index[0] > pd.Timestamp('2020-03-13'):
            COVID = True
        signals.append(scan(priceDF.loc[priceDF.idx < index], COVID=COVID))

    priceDF['signals'] = signals

    if optimizeOnly:
        return priceDF.signals
    else:
        return priceDF
