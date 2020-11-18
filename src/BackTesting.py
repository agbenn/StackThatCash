import pandas as pd;
from utilities import getPercChange

def backTest(backTestDF, shorts=False, closeOnHold=True):
    # completed DF must have buy and sell signals at each date
    
    currentTotal = 0
    purchasePrice = 0
    isLong = False
    isShort = False
    longPositions = 0
    shortPositions = 0

    for index, row in backTestDF.iterrows():
        
        if row['signals'] == 1:
            # buy signal - sell shorts or purchase stock
            if shorts and not isLong and isShort:
                currentTotal += (purchasePrice - row['Close'])
                isShort = False
            if not isLong and not isShort:
                purchasePrice = row['Close']
                isLong = True
                isShort = False
                longPositions += 1
        elif row['signals'] == -1:
            # sell signal - open short position or sell current position
            if not isShort and isLong:
                currentTotal += (row['Close'] - purchasePrice)
                isLong = False
            if shorts and not isShort and not isLong:
                purchasePrice = row['Close']
                isLong = False
                isShort = True
                shortPositions += 1
        elif row['signals'] == 0 and closeOnHold:
            if not isShort and isLong:
                currentTotal += (row['Close'] - purchasePrice)
                isLong = False
            if shorts and not isLong and isShort:
                currentTotal += (purchasePrice - row['Close'])
                isShort = False

    if isLong:
        currentTotal += list(backTestDF.Close)[-1] - purchasePrice
    elif isShort:
        currentTotal += purchasePrice - list(backTestDF.Close)[-1]

    print(str(currentTotal) + ' earned')
    print(str(longPositions) + ' long positions')
    print(str(shortPositions) + ' short positions')

    return currentTotal

def backTestLimits(backTestDF, upsideLimit=.05, downsideLimit=-.03):
    totalInvested = 0
    currentTotal = 0
    purchasePrice = 0
    isFirstPass = True
    isLong = False
    longPositions = 0

    for index, row in backTestDF.iterrows():
        if row['signals'] == 1 and isLong == False:
            purchasePrice = row['Close']
            currentTotal -= purchasePrice
            isLong = True
            longPositions += 1
            if isFirstPass:
                totalInvested = purchasePrice
                isFirstPass = False
        if row['signals'] == 0 and isLong == True:
            currentChange = getPercChange(row['Close'], purchasePrice)
            if currentChange > upsideLimit or currentChange <= downsideLimit:
                currentTotal += (row['Close'])
                isLong = False
        if currentTotal < 0:
            totalInvested += abs(currentTotal)

    ROI = getPercChange(currentTotal, totalInvested)

    print(str(totalInvested) + ' invested')
    print(str(currentTotal) + ' earned')
    print(str(ROI) + ' return on investment')
    print(str(longPositions) + ' long positions')

    return str([currentTotal, totalInvested, ROI])


def getOptimalSignals(priceDF):
    # given a DF tell when to buy and sell optimally (used later for parameter optimization)
    # hold signal for most recent day

    optimalSignals = []
    priceDF['idx'] = range(0, len(priceDF))

    for index in range(len(priceDF)-1):
        nextDay = priceDF.loc[priceDF.idx == index+1, 'Close'].values[0]
        currentDay = priceDF.loc[priceDF.idx == index, 'Close'].values[0]
        percChange = (nextDay - currentDay) / currentDay
        if percChange > .01:
            optimalSignals.append(1)
        elif percChange < .01:
            optimalSignals.append(-1)
        else:
            optimalSignals.append(0)
    
    optimalSignals.append(0)

    priceDF['optimalSignals'] = optimalSignals

    return priceDF



