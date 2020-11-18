import DailyStockData as stocks

x = stocks.getDailyPrice('IBM')
print('all the data')
print(x)

print('close for each day')
print(x.Close)

print('columns for dataframe')
print(x.columns)

print('close on August 1 2019')
print(x.loc[x.index == '2019-08-01'].Close)


