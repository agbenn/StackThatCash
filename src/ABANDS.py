import pandas as pd 
import numpy as np


# Acceleration Bands (ABANDS) - create two lines (high and low) tracking the moving avg
# if stock crosses either high or low band - buy / sell signal (momentum based)

def getDF(priceDF, windowSize=20, scaleFactor=1):

    priceDF['upperBand'] = (priceDF.High * ( 1 + 4 * (priceDF.High - priceDF.Low) / (priceDF.High + priceDF.Low))) * scaleFactor
    priceDF['upperBand'] = priceDF['upperBand'].rolling(windowSize).mean()
    priceDF['lowerBand'] = (priceDF.Low * (1 - 4 * (priceDF.High - priceDF.Low)/ (priceDF.High + priceDF.Low))) * scaleFactor
    priceDF['lowerBand'] = priceDF['lowerBand'].rolling(windowSize).mean()

    return priceDF


def ABANDSDecisionMaker(priceDF, windowSize=5):
    # if buy flag on current date
    priceCheck = priceDF.iloc[-1,:]

    windowSize = windowSize*-1

    if priceCheck.Close >= priceCheck.upperBand or priceCheck.Close <= priceCheck.lowerBand:
        priceDF = priceDF[windowSize:]

        # buy flag
        if priceDF.loc[(priceDF.upperBand <= priceDF.Close)].shape[0] > 0:
            # is close price going further away from or getting closer to upper band
            priceDF['monoCheck'] = priceDF.Close - priceDF.upperBand
            
            # getting further away from lines
            if priceDF.monoCheck.is_monotonic_increasing:
                return 1
            else: 
                # coming back to lines
                if priceDF.monoCheck.is_monotonic_decreasing:
                    return -1
                else:
                    return 0
        elif priceDF.loc[(priceDF.lowerBand >= priceDF.Close)].shape[0] > 0:
            # is close price going further away from or getting closer to lower band
            priceDF['monoCheck'] = priceDF.Close - priceDF.lowerBand
            
            # getting further away
            if priceDF.monoCheck.is_monotonic_decreasing:
                return -1
            else:
                # coming back inside lines
                if priceDF.monoCheck.is_monotonic_increasing:
                    return 1
                else:
                    return 0
        else:
            return 0
    else:
        return 0


def scan(priceDF, ABANDSWindowSize=20, ABANDSScaleFactor=1, decisionWindowSize=5):
    priceDF = getDF(priceDF,ABANDSWindowSize,ABANDSScaleFactor)
    return ABANDSDecisionMaker(priceDF,decisionWindowSize)
    
def getBackTestDF(priceDF, ABANDSWindowSize=20, ABANDSScaleFactor=1, decisionWindowSize=5):
    signals = list(np.zeros(ABANDSWindowSize))
    for index in range(ABANDSWindowSize,len(priceDF)):
        try:
            signals.append(scan(priceDF.loc[0:index], ABANDSWindowSize, ABANDSScaleFactor, decisionWindowSize))
        except Exception as e:
            print('error getting backtesting DF at index: ' + index)
            print('error: ' + str(e))

    print(len(signals))
    print(len(priceDF))

    priceDF['signals'] = signals

    return priceDF

def getOptimizedParameters(priceDFwOptimizedSignals):
    
    currentBest = None
    optimalParameters = {'ABANDSWindowSize':10,'ABANDSScaleFactor':14,'decisionWindowSize':5}

    for ABANDSWindowSize in range(5,15): #x10
        for ABANDSScaleFactor in range(10,18): #x80
            for decisionWindowSize in range(3,7): #x320
                optimized = getBackTestDF(priceDFwOptimizedSignals, ABANDSWindowSize, ABANDSScaleFactor, decisionWindowSize)
                score = abs((priceDFwOptimizedSignals.optimalSignals - optimized).sum())
                print(score)
                if currentBest == None:
                    currentBest = score
                elif currentBest > score:
                    currentBest = score
                    print('new score: ' + currentBest)
                    optimalParameters['ABANDSWindowSize'] = ABANDSWindowSize
                    optimalParameters['ABANDSScaleFactor'] = ABANDSScaleFactor
                    optimalParameters['decisionWindowSize'] = decisionWindowSize

    return {'ABANDS': optimalParameters}

# TODO implement a multi window test to get recency of price movement and make decision based off of 
# when the buy sell signal changed i.e. if lowerband now converging and window is small sell current position but dont sell new
# TODO take into account the magnitude of price change
