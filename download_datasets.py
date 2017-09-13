import pandas as pd
from utils_and_tools import WriteToConsole


def DownloadDataset(object):

    if (object == "iris"):
        WriteToConsole('\nDownloading %s Dataset...' % (object))
        df = pd.read_csv('https://archive.ics.uci.edu/ml/'
                         'machine-learning-databases/iris/iris.data', header=None)
        WriteToConsole('\nSaving %s Dataset...' % (object))
        df.to_csv('./datasets/iris.csv', index=False, encoding = "utf-8")
        WriteToConsole('\nDownload complete.')

    if (object == "wine"):
        WriteToConsole('\nDownloading %s Dataset...' % (object))
        df = pd.read_csv('https://archive.ics.uci.edu/ml/'
                         'machine-learning-databases/wine/wine.data', header=None)
        WriteToConsole('\nSaving %s Dataset...' % (object))
        df.to_csv('./datasets/wine.csv', index=False, encoding = "utf-8")
        WriteToConsole('\nDownload complete.')

    return None

#DownloadDataset('wine')



  # conditional flow uses if, elif, else
#  if(x < y):
#    st= "x is less than y"
#  elif (x == y):
#    st= "x is same as y"
#  else:
#    st= "x is greater than y"
#  print st

#class DownloadDataset(object):
#    def __init__(self, dataset):
#        self.dataset = dataset
#
#        if (self.dataset == "IRIS"):
#            sys.stdout.write('\rDownloading %s Dataset:' % (self.dataset))
#            sys.stdout.flush()
#            df = pd.read_csv('https://archive.ics.uci.edu/ml/'
#                             'machine-learning-databases/iris/iris.data', header=None)
#            df.to_csv('./datasets/iris.csv', index=False, encoding = "utf-8")

#   def GetDataset(self, X, y):
#    class anotherClass(myClass):
#  def method2(self):
#    print "anotherClass method2"
#
#  def method1(self):
#    myClass.method1(self);
#    print "anotherClass method1"
#
#  def method1(self):
#    print "myClass method1"
#
#  def method2(self, someString):
#    print "myClass method2: " + someString