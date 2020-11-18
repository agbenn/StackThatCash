import pandas as pd
import numpy as np


def getDF(priceDF, windowSize=14):

    priceDF['posDM'] = priceDF.High.diff().dropna()
    priceDF['negDM'] = priceDF.Low.diff().dropna()

    # normalize the directional vectors
    priceDF.loc[(priceDF.posDM < 0) & (priceDF.negDM < 0),['posDM','negDM']] = 0
    priceDF.loc[(priceDF.posDM < priceDF.negDM), 'posDM'] = 0
    priceDF.loc[(priceDF.posDM > priceDF.negDM), 'negDM'] = 0

    def customWilderSmoothing(value, offsetValue, index):
        return (offsetValue - (offsetValue / index))  + (value)

    def trueRange(valueHigh, valueLow, offsetValueHigh, offsetValueLow):
        return max((valueHigh-valueLow), (valueHigh-offsetValueHigh), (offsetValueLow-valueLow))

    WilderSmoothing = np.vectorize(customWilderSmoothing)
    getTR = np.vectorize(trueRange)

    # set one and one offset dataframe
    priceDF = priceDF[1:]
    offsetDF = priceDF[1:]
    priceDF = priceDF[:-1]
    priceDF['TR'] = getTR(priceDF.High, priceDF.Low, offsetDF.High, offsetDF.Low)
    offsetDF = priceDF[1:]
    priceDF = priceDF[:-1]

    indexSeries = np.arange(len(priceDF)) + 1

    priceDF['+DM'] = WilderSmoothing(priceDF['posDM'], offsetDF['posDM'], indexSeries)
    priceDF['-DM'] = WilderSmoothing(priceDF['negDM'], offsetDF['negDM'], indexSeries)
    priceDF['TR'] = WilderSmoothing(priceDF['TR'], offsetDF['TR'], indexSeries)

    priceDF['+DI'] = (priceDF['+DM']/priceDF['TR'])*100
    priceDF['-DI'] = (priceDF['-DM']/priceDF['TR'])*100
        
    priceDF['DIdiff'] = ((priceDF['+DI']) - (priceDF['-DI'])).abs()
    priceDF['DIsum'] = ((priceDF['+DI']) + (priceDF['-DI']))

    # directional movement index should be 0-100
    priceDF['DX'] = (priceDF['DIdiff'] / priceDF['DIsum']) * 100

    priceDF['DX'] = priceDF['DX'].fillna(0)

    #TODO clean up this bit of logic
    averagedDX = []
    prevADX = 0

    for index in range(0, len(priceDF.DX)):
        x = index + 1
        ADX = ((prevADX * ( x - 1) ) +  priceDF.DX[index]) / x
        averagedDX.append(ADX)
        prevADX = ADX

        
    priceDF['ADX'] = averagedDX

    priceDF = priceDF.drop(columns=['posDM', 'negDM', 'TR', '+DM', '-DM', 'DIdiff', 'DIsum', 'DX'])

    return priceDF



def ADXDecisionEngine(priceDF, windowSize=5, rigor=.5):
    # check if ADX is indicating
    # is ADX increasing or decreasing
    # which indicator buy or sell
    # what is the movement

    windowSize = windowSize*-1
    
    priceWindow = priceDF[windowSize:]

    if priceDF.ADX[-1] > 100*rigor:
        if priceWindow.ADX.is_monotonic_increasing:
            if priceDF.iloc[-1,'+DI'] > priceDF.iloc[-1,'-DI']:
                return 1
            else:
                return -1
    return 0

def scan(priceDF, ADXWindowSize=14, decisionWindowSize=5, rigor=.5):
    priceDF = getDF(priceDF, ADXWindowSize)
    return ADXDecisionEngine(priceDF,decisionWindowSize,rigor)  

def getBackTestDF(priceDF, ADXWindowSize=14, decisionWindowSize=5, rigor=.5):
    signals = list(np.zeros(ADXWindowSize))
    for index in range(ADXWindowSize,len(priceDF)):
        try:
            signals.append(scan(priceDF.loc[0:index], ADXWindowSize, decisionWindowSize, rigor))
        except Exception as e:
            print('error getting backtesting DF at index: ' + index)
            print('error: ' + str(e))

    print(len(signals))
    print(len(priceDF))

    priceDF['signals'] = signals

    return priceDF

def getOptimizedParameters(priceDFwOptimizedSignals):
    
    currentBest = None
    optimalParameters = {'windowSize':10,'ADXWindowSize':14,'decisionWindowSize':5,'rigor':.5}

    for windowSize in range(5,15): #x10
        for ADXWindowSize in range(10,18): #x80
            for decisionWindowSize in range(3,7): #x320
                for rigor in range(.5,.9,.1):   #x1260
                    optimized = getBackTestDF(priceDFwOptimizedSignals, ADXWindowSize, decisionWindowSize, rigor)
                    score = abs((priceDFwOptimizedSignals.optimalSignals - optimized).sum())
                    print(score)
                    if currentBest == None:
                        currentBest = score
                    elif currentBest > score:
                        currentBest = score
                        print('new score: ' + currentBest)
                        optimalParameters['windowSize'] = windowSize
                        optimalParameters['ADXWindowSize'] = ADXWindowSize
                        optimalParameters['decisionWindowSize'] = decisionWindowSize
                        optimalParameters['rigor'] = rigor

    return {'ADX': optimalParameters}



