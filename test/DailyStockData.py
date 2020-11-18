from pandas_datareader import data as pdr
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
import numpy as np
import sys, os

yf.pdr_override()

currentDate = (date.today() + timedelta(days=1))

def getDaytoDayPercChange(ticker, start_date="2000-01-01"):
    try:
        tickerData = pdr.get_data_yahoo(ticker, start=start_date, end=currentDate)
        newData = []
        for count in range(1,tickerData.shape[0]):
            newData.append((tickerData.Close.iloc[count]-tickerData.Close.iloc[count-1])/tickerData.Close.iloc[count-1])
        return pd.DataFrame(newData, columns=[ticker])
    except:
        print('symbol not listed')

def getDaytoDayDollarChange(ticker, start_date="2000-01-01"):
    try:
        tickerData = pdr.get_data_yahoo(ticker, start=start_date, end=currentDate)
        newData = []
        for count in range(1,tickerData.shape[0]):
            newData.append((tickerData.Close.iloc[count]-tickerData.Close.iloc[count-1])/tickerData.Close.iloc[count-1])
        return pd.DataFrame(newData, columns=[ticker])
    except:
        print('symbol not listed')

def getDailyPrice(ticker, start_date="2000-01-01"):
    try:
        return pdr.get_data_yahoo(ticker, start="2000-01-01", end=currentDate)
    except:
        print('symbol not listed')

def getOptionsChain(ticker, calls_or_puts):
  '''
  This searches all possible expiry dates and finds contracts.
  '''

  #suppress prints b/c datareader is annoying then restore printing so this helps

  finaldf = pd.DataFrame()
  ticker = yf.Ticker(ticker)
  stock_price = data.get_data_yahoo(ticker, end_date = date.today())['Close'][-1]
  for opt_date in ticker.options:
    opt = ticker.option_chain(opt_date)
    if calls_or_puts == 'puts':
      opt.puts.insert(0,'opt_date', opt_date)
      finaldf = finaldf.append(opt.puts)
    else:
      opt.calls.insert(0,'opt_date', opt_date)
      finaldf = finaldf.append(opt.calls)
  return finaldf, stock_price


def getUnusualOptionsActivity(ticker, call_or_puts):
    returned = getOptionsChain(ticker, call_or_puts)

    # Do some final formatting changes
    returned = returned.drop(columns = ['contractSymbol'])
    if calls_or_puts == 'puts':
        returned.insert(3, 'dist OTM', stock_price - returned['strike'])
    else:
        returned.insert(3, 'dist OTM', returned['strike'] - stock_price)

    returned.insert(4, '% OTM', returned['dist OTM']/stock_price*100)
    returned['value'] = returned['openInterest']*returned['lastPrice']*100

    fileName = str(date.today()) + '_' + symbol +'_' + call_or_puts + '.csv.gz'

    return returned