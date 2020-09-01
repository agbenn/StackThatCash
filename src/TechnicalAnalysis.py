



# Acceleration Bands (ABANDS) - create two lines (high and low) tracking the moving avg
# if stock crosses either high or low band - buy / sell signal (momentum based)

def ABANDS(priceDF, windowSize, scaleFactor=1):

    priceDF['upperBand'] = (priceDF.High * ( 1 + 4 * (priceDF.High - priceDF.Low) / (priceDF.High + priceDF.Low))) * scaleFactor
    priceDF['upperBand'] = priceDF['upperBand'].rolling(windowSize).mean()
    priceDF['lowerBand'] = (priceDF.Low * (1 - 4 * (priceDF.High - priceDF.Low)/ (priceDF.High + priceDF.Low))) * scaleFactor
    priceDF['lowerBand'] = priceDF['lowerBand'].rolling(windowSize).mean()

    return priceDF

