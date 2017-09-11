import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from load_datasets import LoadDataset


def Scale(X_train, X_test, t="std"):
    """ Bring features onto the same scale

    t = "std":   center feature columns at mean 0 with
                 standard deviation at 1 so the feature
                 column take the form of a normal
                 distribution. Good for outliers.
    t = "norm":  rescales feature columns to a range
                 between 0 and 1. Good when a bounded
                 interval is needed.
    """

    # Standarization
    if (t == "std"):

        # Instantiate object
        sc = StandardScaler()
        # Return fitted and transformed objects
        return sc.fit_transform(X_train), sc.transform(X_test)

    # Normalization
    if (t == "norm"):

        # Instantiate object
        mms = MinMaxScaler()
        # Return fitted and transformed objects
        return mms.fit_transform(X_train), mms.transform(X_test)

    else:
        print("Incorrect type parameter")



def EncodeClassLabel(column):
    """ Encode class label """
    # df['classlabel'] = EncodeClassLabel(df['classlabel'])

    # Instantiate object
    le = LabelEncoder()
    # Return fitted and transformed object
    return le.fit_transform(column)


def EncodeNominalFeature(df, encode_column, classlabel_column):
    # Usage: df = EncodeNominalFeature(df, df[['nominal_color']], 'classlabel')
    # df: dataframe with nomina feature
    # encode_column: nominal feature column to one-hot encode
    # classlabel_column: name of class label for supervised classifiers

    # encode dummy features from encode_column
    encoded_features = pd.get_dummies(encode_column)
    # concatenate original dataframe with new dummy features horizontally
    df = pd.concat([df, encoded_features], axis=1)
    # get np array with the names of columns of the concatenated dataframe
    df_column_names = df.columns.values
    # get index of class label column from np array. We can also use this
    # below but it's slower:
    # index_of_classlabel_column = np.flatnonzero(df_column_names == classlabel_column)[0]
    index_of_classlabel_column = next(i for i, df_column_names_i in enumerate(df_column_names) if df_column_names_i == classlabel_column)
    # delete the class label item from the np array
    df_column_names1 = np.delete(df_column_names, index_of_classlabel_column)
    # append the class label item to the end of the np array
    df_column_names2 = np.append(df_column_names1, classlabel_column)
    # rearrange the columns of the dataframe by using the new np array
    df1 = df.reindex_axis(df_column_names2, axis=1)
    # delete the encode_column from the returning dataframe
    df1.drop(encode_column, inplace=True, axis=1)
    # return a new dataframe with the nominal feature encoded and cleaned
    return df1


def MapOrdinalFeature(column, mapping):
    #    mapping = {
    #               'S': 1,
    #               'M': 2,
    #               'L': 3,
    #               'XL': 4,
    #               'XXL': 5}
    #    df['ordinal_size'] = MapOrdinalFeature(df['ordinal_size'], mapping)
    return column.map(mapping)


def ReverseMapOrdinalFeature(column, mapping):
    #    mapping = {
    #               'S': 1,
    #               'M': 2,
    #               'L': 3,
    #               'XL': 4,
    #               'XXL': 5}
    #    df['ordinal_size'] = ReverseMapOrdinalFeature(df['ordinal_size'], mapping)
    inv_mapping = {v: k for k, v in mapping.items()}
    return column.map(inv_mapping)


def HandleMissingData(df):

    # Check whether Dataframe has missing values
    if (df.isnull().values.any() is True):
        pass

#from sklearn.preprocessing import Imputer
#
#imr = Imputer(missing_values='NaN', strategy='mean', axis=0)
#imr = imr.fit(df)
#imputed_data = imr.transform(df.values)
#imputed_data


# conditional flow uses if, elif, else
#  if(x < y):
#    st= "x is less than y"
#  elif (x == y):
#    st= "x is same as y"
#  else:
#    st= "x is greater than y"
#  print st
