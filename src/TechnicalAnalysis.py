



# Acceleration Bands (ABANDS) - create two lines (high and low) tracking the moving avg
# if stock crosses either high or low band - buy / sell signal (momentum based)

def ABANDS(priceDF, windowSize, scaleFactor=1):

    priceDF['upperBand'] = (priceDF.High * ( 1 + 4 * (priceDF.High - priceDF.Low) / (priceDF.High + priceDF.Low))) * scaleFactor
    priceDF['upperBand'] = priceDF['upperBand'].rolling(windowSize).mean()
    priceDF['lowerBand'] = (priceDF.Low * (1 - 4 * (priceDF.High - priceDF.Low)/ (priceDF.High + priceDF.Low))) * scaleFactor
    priceDF['lowerBand'] = priceDF['lowerBand'].rolling(windowSize).mean()

    

    # if buy flag on current date
    priceCheck = priceDF.iloc[-1,:]

    if priceCheck.Close >= priceCheck.upperBand or priceCheck.Close <= priceCheck.lowerBand:
        # TODO further logic on window selection size for converging / diverging logic
        # potentially multi test on multiple window sizes to determine short term vs long term play / *** when to sell ***
        priceDF = priceDF[-5:]

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
