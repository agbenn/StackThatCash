import DailyStockData as stocks
import TechnicalAnalysis as TA

x = stocks.getDailyPrice('IBM')
print('all the data')
print(x)

print('close for each day')
print(x.Close)

print('columns for dataframe')
print(x.Close)

print('close on August 1 2019')
print(x.loc[x.index == '2019-08-01'].Close)

result = TA.ABANDS(x, 20)

print(result)
