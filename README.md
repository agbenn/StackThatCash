# Stack That Cash
Comprehensive TA functions in Python. [Source of TA functions](https://www.tradingtechnologies.com/xtrader-help/x-study/technical-indicator-definitions/list-of-technical-indicators/)

### Dependencies - 
`pip install pandas-datareader`  
`pip install yfinance`

## Getting started
- TA functions defined in `src` directory
- Simple use case of functions in `example` directory

## Good to Know

Every function returns a Pandas Dataframe. Pandas is a god send and will allow you god powers

### Pandas code basics-

#### `df` == dataframe  
the standardized unit of data transactions in python


#### `df.loc[]` -  
ie. `df.loc[df.index == '2019-08-01']`  

Format -  
`df.loc[df.someRow (some boolean operation to select the data you want)]`  

`df.loc[df.someColumn (some boolean combination with | & operators and heavy parenthisis to separate a combo bool]`

#### `df.iloc[row,col]` -    
used for index operators

#### New column creation-
`df['newColumn'] = df.someColumn * df.otherColumn`  
not like this-   
`df.newColumn = some shit`

#### if you are looking at a for loop / while loop situation look at documentation for numpy.vectorize first: 
https://numpy.org/doc/stable/reference/generated/numpy.vectorize.html
`

## TODO-
1. Work on the Options info in `showMeWhatYouHaveGot.py`  
2. Organize better - 
- separate individual/grouped functions into classes
- name above classes/functions based off which indicator they are

