look at the test file: showMeWhatYouHaveGot.py
(working on the options info)

import the DailyStockData file

every function returns a Pandas Dataframe 

Pandas is a god send and will allow you god powers

the main commands are in the test file 

df == dataframe the standardized unit of data transactions in python

df.loc[df.someColumn (some boolean operation to select the data you want)]

df.loc[df.someColumn (some boolean combination with | & operators and heavy parenthisis to separate a combo bool]

df.iloc[row,col] (for index operators)

vectorized operations of everything:

has to look like this for new column creation
df['newColumn'] = df.someColumn * df.otherColumn
not like this 
df.newColumn = some shit

if you are looking at a for loop / while loop situation look at documentation for numpy.vectorize first: 
https://numpy.org/doc/stable/reference/generated/numpy.vectorize.html



