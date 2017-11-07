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
