#Import packages
import pandas as pd
from mlxtend.frequent_patterns import apriori

#read data
df = pd.read_csv(')
df.dropna(inplace = True)
df.drop(['StockCode'], axis = 1, inplace = True)
df.Description.str.strip()

#Join items based on InvoiceNo
df2 = df.groupby(['InvoiceNo'])['Description'].transform(lambda x: '|'.join(x))
df2.drop_duplicates(inplace = True)

#Create dummy variables
df3 = df2.str.get_dummies().reset_index(drop = True)

#Find probability distribution for a given item set
items = [' 4 PURPLE FLOCK DINNER CANDLES' , '3 DRAWER ANTIQUE WHITE WOOD CABINET']
df4 = df3[(df3[items] == 1).all(axis = 1)]

#Given items are present, how common is a combination with another item within all of the data
distribution_total  = df4.sum(axis = 0) / len(df3.index)
distribution_total = distribution_total[distribution_total != 0]

#Given items are present, how common is a combination with another item within subset of data
distribution_subset = df4.sum(axis = 0) / len(df4.index)
distribution_subset = distribution_subset[distribution_subset != 0]

