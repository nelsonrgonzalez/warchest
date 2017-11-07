"""
    Warchest: Data management and automation GUI for Machine Learning projects
    Created September 2017
    Copyright (C) Nelson R Gonzalez

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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
