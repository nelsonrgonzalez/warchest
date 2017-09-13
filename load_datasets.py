import pandas as pd
from utils_and_tools import WriteToConsole


def LoadDataset(object):

    if (object == "iris"):
        WriteToConsole('\nLoading %s Dataset...' % (object))
        df = pd.read_csv('./datasets/iris.csv')
        WriteToConsole('\nLoading complete.')
        return df

    if (object == "eda"):
        WriteToConsole('\nLoading %s Dataset...' % (object))
        df = pd.read_csv('./datasets/eda.csv')
        WriteToConsole('\nLoading complete.')
        return df

    if (object == "wine"):
        WriteToConsole('\nLoading %s Dataset...' % (object))
        df = pd.read_csv('./datasets/wine.csv')
        WriteToConsole('\nLoading complete.')
        return df


# conditional flow uses if, elif, else
#  if(x < y):
#    st= "x is less than y"
#  elif (x == y):
#    st= "x is same as y"
#  else:
#    st= "x is greater than y"
#  print st
