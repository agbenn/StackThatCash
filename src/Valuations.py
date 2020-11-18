from pandas_datareader import data as pdr
import yfinance as yf
import pandas as pd
from datetime import date, timedelta, datetime
import requests
import numpy as np
from io import StringIO
from dateutil.relativedelta import relativedelta
import dateutil.parser


class Stock():
    """   financials = None
    financialPeriod = None
    intrinsicValuations = None
    relativeValuations = None"""
    
    def __init__(self, ticker):
        #self.financials = self.getFinancials(ticker)
        self.financials = self.getFinancialsLocal(ticker)
        self.financials = self.cleanFinancials(self.financials)
        print(self.financials.tail(1))
        self.financialPeriod = self.financials.head(1)
        #self.marketValue = self.calculateFairMarketValue()
        #self.expectedGrowthRate = self.calculateGrowthRate()
        #self.setGrowthColumn()
        self.intrinsicValuations = IntrinsicValuations(self.financialPeriod)
        self.fairMarketValue = self.intrinsicValuations.calculateFairMarketValue(self.stock.financials.loc[self.stock.financials.periodenddate <= self.stock.financialPeriod.periodenddate])
        self.relativeValuations = RelativeValuations(self.financialPeriod)
        
    def getFinancialsLocal(self, ticker):
        filePath = 'financialFilings/' + ticker + '.csv'
        return pd.read_csv(filePath, index_col=False)
        
    def getFinancials(self, ticker):
        
        try:
            print('getting ' + ticker + 'financial filings')
            
            requestURL = "https://datafied.api.edgar-online.com/v2/corefinancials/qtr.json?primarysymbols=" + ticker + "&numperiods=52&debug=true&appkey=8dcfc9576bd6bdbdd69bf02811cdbfc7"
            x = requests.get(requestURL)
            initDataFrame = pd.DataFrame.from_dict(x.json().get('result').get('rows')[0].get('values')).transpose()

            for increment in range(1,len(x.json().get('result').get('rows'))):
                z = pd.DataFrame.from_dict(x.json().get('result').get('rows')[increment].get('values')).transpose().loc['value',:]
                initDataFrame = initDataFrame.append(z) 

            initDataFrame.columns = initDataFrame.loc['field',:]
            initDataFrame = initDataFrame.drop('field')

            return initDataFrame
            
        except:
            raise ValueError('no data was available for ' + ticker)           
    
    def getGrowthRateColumn(self):
        allEbit = []
        prevVal = None

        for each in self.financials.ebit:
            if prevVal == None:
                prevVal = each
                allEbit.append(0)
            else:
                allEbit.append((each-prevVal)/prevVal)

        # need to project next year growth - current avg growth for 3 years previous 
        ### TODO: find different ways of projecting different growth rates - ARIMA etc
        
        #allEbit.append((np.array(allEbit[-3:]).mean()))
        return allEbit
    
    def cleanFinancials(self, data):
        data.head(5)
        data = data.replace(0,np.nan)
        data = data.fillna(method='bfill')
        data = data.fillna(method='ffill')
        data = data.dropna(axis='columns')
        print(data.head(5))
        def convertToDatetime(date):
            return dateutil.parser.parse(date)
        func = np.vectorize(convertToDatetime)
        data.periodenddate = func(data.periodenddate)
        print(data.shape)
        x = self.getGrowthRateColumn()
        print(len(x))
        data['ebitGrowthRate'] = x
        return data
    
    # for any date given - set the financial period (Quarterly)
    def setPeriod(self, date):
        date = dateutil.parser.parse(date)
        financialPeriod = self.financials.loc[self.financials.fiscalyear == date.year]
        financialPeriod = financialPeriod.loc[financialPeriod.periodenddate.month >= date.month]    
        # multiple period - need to find closest to current (min) 
        keyValue = min(financialPeriod.periodenddate, key=lambda x: abs(x - date))
        financialPeriod = self.financials.loc[financialPeriod.periodenddate == keyValue]
        self.financialPeriod = self.financials.loc[self.financials.periodenddate == financialPeriod.periodenddate]
        self.intrinsicValuations.setVariables()
        self.fairMarketValue = self.intrinsicValuations.calculateFairMarketValue(self.stock.financials.loc[self.stock.financials.periodenddate <= self.stock.financialPeriod.periodenddate])
    
# only calculated for a specific period
# DCF Intrinsic valuation metrics
class IntrinsicValuations:
    
    ## TODO need to catch an error for incomplete data sets -> work through many to see how many fields need to be filled / dropped 

    def __init__(self, data):
        self.WACC = self.getWACC(data)
        self.unleveredFCF = self.getUnleveredFCF(data)
        self.riskFreeRate = self.getRiskFreeRate(data)

    # set global IntrinsicValuation variables
    def setVariables(self):
        self.WACC = self.getWACC()
        self.unleveredFCF = self.getUnleveredFCF()
        self.riskFreeRate = self.getRiskFreeRate()

    # unlevered free cash flow
    def getUnleveredFCF(self, data):
        print('calculating unlevered free cash flow')
        return data.ebit - (data.ebit - data.netincome + data.interestexpense) + data.cfdepreciationamortization - data.capitalexpenditures - (data.totalassets - data.cashandcashequivalents - data.totalliabilities)

    #market Capitalization
    def getMarketCapitalization(self, data):
        print('getting market capitalization')
        print(data.columns)
        START = data.periodenddate
        END = data.periodenddate + timedelta(days=1)
        
        print(data.periodenddate)
        
        stockPrice = pdr.get_data_yahoo(str(data.primarysymbol.values[0]), start=pd.to_datetime(str(START.values[0])).strftime('%Y-%m-%d'), end=pd.to_datetime(str(END.values[0])).strftime('%Y-%m-%d'))

        return data.commonstock * stockPrice.Close

    # get risk free rate from 3 month treasury yield 
    # ***TODO create a function to match the growth rate such that the price is most accurately reflected by the Model
    # optimize risk free rate / (growth rate)
    def getRiskFreeRate(self):
        print('getting risk free rate')
        return (pd.read_csv(StringIO((requests.get("https://www.quandl.com/api/v3/datasets/USTREASURY/YIELD.csv?api_key=z52BFANNtWQyrvYyEgsu")).text)))['3 MO'].iloc[0]

    # get market growth decrease for a quarter
    def getQuarterlyMarketReturn(self, index, data):
        print('getting quarterly market return')

        START = data.periodenddate - relativedelta(months=+3) + timedelta(days=1)
        STARTSEND = START + datetime.timedelta(days=1)
        END = data.periodenddate
        ENDSEND = END + datetime.timedelta(days=1)

        index = index.lower()

        if 'sp' in index:
            start = pdr.get_data_yahoo('^GSPC', start=START, end=STARTSEND)
            end = pdr.get_data_yahoo('^GSPC', start=END, end=ENDSEND)
        elif 'dow' in index:
            start = pdr.get_data_yahoo('^DJI', start=START, end=STARTSEND)
            end = pdr.get_data_yahoo('^DJI', start=END, end=ENDSEND)
        elif 'nas' in index:
            start = pdr.get_data_yahoo('^IXIC', start=START, end=STARTSEND)
            end = pdr.get_data_yahoo('^IXIC', start=END, end=ENDSEND)
        elif 'nyse' in index:
            start = pdr.get_data_yahoo('^NYA', start=START, end=STARTSEND)
            end = pdr.get_data_yahoo('^NYA', start=END, end=ENDSEND)

        growth = (end.Close - start.Close) / start.Close

        return growth

    # get covariance between stock and index
    def getCovarianceOfAStock(self, index, data):
        print('getting stock covariance')

        START = data.periodenddate - relativedelta(months=+3) + timedelta(days=1)
        END = data.periodenddate + timedelta(days=1)

        index = index.lower()

        if 'sp' in index:
            idx = pdr.get_data_yahoo('^GSPC', start=START, end=END)
        elif 'dow' in index:
            idx = pdr.get_data_yahoo('^DJI', start=START, end=END)
        elif 'nas' in index:
            idx = pdr.get_data_yahoo('^IXIC', start=START, end=END)
        elif 'nyse' in index:
            idx = pdr.get_data_yahoo('^NYA', start=START, end=END)

        stock = pdr.get_data_yahoo(data.primarysymbol, start=START, end=END)

        df = pd.concat([stock['Close'],idx['Close']], axis=1)
        df.columns = ['stock', 'index']

        return (df.cov()).iloc[0,1]

    # get variance of a market index 
    def getVarianceOfAMarket(self, index, data):
        print('getting market variance')

        START = data.periodenddate - relativedelta(months=+3) + timedelta(days=1)
        END = data.periodenddate + timedelta(days=1)

        index = index.lower()

        if 'sp' in index:
            idx = pdr.get_data_yahoo('^GSPC', start=START, end=END)
        elif 'dow' in index:
            idx = pdr.get_data_yahoo('^DJI', start=START, end=END)
        elif 'nas' in index:
            idx = pdr.get_data_yahoo('^IXIC', start=START, end=END)
        elif 'nyse' in index:
            idx = pdr.get_data_yahoo('^NYA', start=START, end=END)

        return idx.Close.var()

    # get beta for a stock 
    def getBeta(self, index, data):
        print('getting beta of the stock')
        return self.getCovarianceOfAStock(data.periodenddate,index,data.primarysymbol)/(data.periodenddate,index)

    # cost of equity (required rate of return)
    def getCostOfEquity(self, data):
        print('getting cost of equity')
        return (self.getRiskFreeRate() + ((self.getBeta(data.periodenddate,data.primaryexchange,data.primarysymbol)*(self.getQuarterlyMarketReturn(data.periodenddate) - self.getRiskFreeRate()))))

    # get value of enterprise capital 
    def getValueOfEnterpriseCapital(self, data):
        print('getting value of enterprise capital')
        return ((data.totalassets - data.totalliabilities) + data.totallongtermdebt)

    # get cost of debt - the rate a company pays on its debt
    def getCostOfDebt(self, data):
        print('getting cost of debt')
        return data.totalinterest / data.totaldebt

    # average maturity of debt ***** ASSUMPTION ***** https://pocketsense.com/average-maturity-debt-7982282.html
    def getAverageMaturityOfDebt(self):
        print('getting average maturity of debt')
        return (7.2 + 13.7)/2

    # get market value of debt 
    def getMarketValueOfDebt(self, data):
        print('getting market value of debt')
        costOfDebt = getCostOfDebt(data.financialPeriod)
        return data.totalinterest*((1-(1/(1+(costOfDebt^getAverageMaturityOfDebt()))))/costOfDebt)+(data.financialPeriod.totaldebt/(1+(costOfDebt^getAverageMaturityOfDebt())))

    # get tax expense
    def getTaxExpense(self, data):
        print('getting tax expense')
        return (data.netincome - data.interestexpense)

    # get tax rate
    def getTaxRate(self, data):
        print('getting tax rate')
        return (data.ebit - (data.netincome - data.interestexpense))/(data.ebit + data.interestexpense)

    #get WACC - the minimum return that a company must earn on an existing asset base to satisfy its creditors, owners, and other providers of capital
    def getWACC(self, data):
        print('calculating Weighted Average Capital Contribution')
        return ((self.getMarketCapitalization(data) / self.getValueOfEnterpriseCapital(data)) * self.getCostOfEquity(data)) + (((self.getMarketValueOfDebt(data)/self.getValueOfEnterpriseCapital(data))*self.getCostOfDebt(data)) * (1-self.getTaxRate(data)))

    # get terminal value for fair market value calculation
    def getTerminalValue(self, data):
        print('getting terminal value')
        return (self.getUnleveredFCF(data)/(1+self.riskFreeRate)/(self.getWACC(data)-self.riskFreeRate))

    # fair market value with for DCF valuation with terminal value based on perpetual growth rate tied to market via WACC
    # must pass multiple values into data
    def calculateFairMarketValue(self, data): 
        print('getting fair market value')
        allDCFs = []

        for each in data:
            unleveredFCF = self.getUnleveredFCF(each)
            WACC = getWACC(each)
            allDCFs.append((unleveredFCF[each] / ((1-riskFreeRate)**(each+1))))
        allDCFs = np.array(allDCFs).sum() + getTerminalValue()

        return allDCFs

    
# RELATIVE VALUATION METRICS
# need to set a period to get data from i.e. what was market value on x date, what were all attributes on x date

class RelativeValuations:
    
    def __init__(self, data):
        self.bookValue = self.getBookValue(data)
        self.EPS = self.getEPS(data)
        self.ROE = self.getROE(data)
        self.DebtToEquity = self.getDebtToEquity(data)
        self.CurrentRatio = self.getCurrentRatio(data)
        self.EVToEBITDA = self.getEVToEBITDA(data)
        self.PriceToFCF = self.getPriceToFCF(data)
        self.InterestCoverage = self.getInterestCoverageRatio(data)
    
    # book value
    def getBookValue(self, data):
        return (data.totalassets - data.totalliabilities) / data.commonstock

    # eps
    def getEPS(self, data):
        return data.netincomeapplicabletocommon / data.commonstock

    # return on equity -> looking for above >20%
    def getROE(self, data):
        return data.netincome / (data.totalassets - data.totalliabilities)

    # debt to equity - less than one ideal
    def getDebtToEquity(self, data):
        return data.totalliabilities / (data.totalassets - data.totalliabilities) 

    # current ratio
    def getCurrentRatio(self, data):
        return data.totalassets / data.totalliabilities 

    # EV / EBITDA
    def getEVToEBITDA(self, data):
        return (self.getMarketCapitalization(data.commonstock, data.periodenddate, data.primarysymbol) + data.totallongtermdebt - data.cashandcashequivalents) / data.ebit

    # price to free cash flow
    def getPriceToFCF(self, data):
        return self.getMarketCapitalization(data.commonstock, data.periodenddate, data.primarysymbol) / (data.cashfromoperatingactivities - data.capitalexpenditures)

    # interest coverage ratio
    def getInterestCoverageRatio(self, data):
        return data.ebit / data.interestexpense

        
