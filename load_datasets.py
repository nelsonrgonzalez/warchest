import pandas as pd
from toolbox import write_to_console


def load_dataset(obj):

    if (obj == "iris"):
        write_to_console('\nLoading %s Dataset...' % (obj))
        df = pd.read_csv('./datasets/iris.csv')
        write_to_console('\nLoading complete.')
        return df

    if (obj == "eda"):
        write_to_console('\nLoading %s Dataset...' % (obj))
        df = pd.read_csv('./datasets/eda.csv')
        write_to_console('\nLoading complete.')
        return df

    if (obj == "wine"):
        write_to_console('\nLoading %s Dataset...' % (obj))
        df = pd.read_csv('./datasets/wine.csv')
        write_to_console('\nLoading complete.')
        return df
