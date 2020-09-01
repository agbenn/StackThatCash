

def bandedDecisionMaker(priceDF, windowSize=5):
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


# TODO implement a multi window test to get recency of price movement and make decision based off of 
# when the buy sell signal changed i.e. if lowerband now converging and window is small sell current position but dont sell new
# TODO take into account the magnitude of price change
