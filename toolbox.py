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

import sys
import sqlite3
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler


def scale(X_train, X_test, scaling="std"):
    """ Bring features onto the same scale

    scaling = "std":   center feature columns at mean 0 with
                       standard deviation at 1 so the feature
                       column take the form of a normal
                       distribution. Good for outliers.
    scaling = "norm":  rescales feature columns to a range
                       between 0 and 1. Good when a bounded
                       interval is needed.
    """

    # Standardization
    if (scaling == "std"):
        sc = StandardScaler()
        return sc.fit_transform(X_train), sc.transform(X_test)

    # Normalization
    if (scaling == "norm"):
        mms = MinMaxScaler()
        return mms.fit_transform(X_train), mms.transform(X_test)
    else:
        print("Incorrect type parameter")


def exec_qry(qry, parameters=()):

    db_filename = 'warchest.db'

    with sqlite3.connect(db_filename) as conn:
        cursor = conn.cursor()
        qry_result = cursor.execute(qry, parameters)
        conn.commit()
    return qry_result


def exec_insert_qry(qry, parameters=()):

    db_filename = 'warchest.db'

    with sqlite3.connect(db_filename) as conn:
        cursor = conn.cursor()
        cursor.execute(qry, parameters)
        conn.commit()
    return cursor.lastrowid


def write_to_console(obj):

    sys.stdout.write(obj)
    sys.stdout.flush()
    return None


def CleanHTML(html):
    """
    Copied from NLTK package.
    Remove HTML markup from the given string.

    :param html: the HTML string to be cleaned
    :type html: str
    :rtype: str
    """
    # Usage
    # html = GetWebpage('http://python.org/' , output="s")
    # clean = CleanHTML(html)
    # Freq_dist_nltk=nltk.FreqDist(tokens)
    # Freq_dist_nltk.plot(50, cumulative=False)

    import re

    # First we remove inline JavaScript/CSS:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
    # Then we remove html comments. This has to be done before removing regular
    # tags since comments can contain '>' characters.
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
    # Next we can remove the remaining tags:
    cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
    # Finally, we deal with whitespace
    cleaned = re.sub(r"&nbsp;", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    return cleaned.strip()


def check_platform():

    from sys import platform as _platform
    if _platform == "linux" or _platform == "linux2":
        # linux
        return 'linux'
    elif _platform == "darwin":
        # MAC OS X
        return 'mac'
    if "win" in _platform:
        # Windows
        return 'windows'


def is_float_series_integer(series):

    for i, row in series.iteritems():
        if series[i].is_integer() is False:
            return False
    return True


def is_integer_series_natural(series):

    for i, row in series.iteritems():
        if (series[i] >= 0) is False:
            return False
    return True


def sorted_by_second_item(obj):

    def return_second_item(item):
        return item[1]

    return sorted(obj, key=return_second_item)


def is_castable(series, type_to_cast):

    min_value = series.min()
    max_value = series.max()

    #if np.dtype(series) == "float16":
    if type_to_cast == "int8":  # Byte (-128 to 127)
        if min_value < -128 or max_value > 127:
            return False
        else:
            return True
    elif type_to_cast == "int16":  # Integer (-32768 to 32767)
        if min_value < -32768 or max_value > 32767:
            return False
        else:
            return True
    elif type_to_cast == "int32":  # Integer (-2147483648 to 2147483647)
        if min_value < -2147483648 or max_value > 2147483647:
            return False
        else:
            return True
    elif type_to_cast == "int64":  # Integer (-9223372036854775808 to 9223372036854775807)
        if min_value < -9223372036854775808 or max_value > 9223372036854775807:
            return False
        else:
            return True
    if type_to_cast == "uint8":  # Unsigned integer (0 to 255)
        if min_value < 0 or max_value > 255:
            return False
        else:
            return True
    elif type_to_cast == "uint16":  # Unsigned integer (0 to 65535)
        if min_value < -0 or max_value > 65535:
            return False
        else:
            return True
    elif type_to_cast == "uint32":  # Unsigned integer (0 to 4294967295)
        if min_value < 0 or max_value > 4294967295:
            return False
        else:
            return True
    elif type_to_cast == "uint64":  # Unsigned integer (0 to 18446744073709551615)
        if min_value < 0 or max_value > 18446744073709551615:
            return False
        else:
            return True
    elif type_to_cast == "float16":  # Half precision float: sign bit, 5 bits exponent, 10 bits mantissa
        return True
    elif type_to_cast == "float32":  # Single precision float: sign bit, 8 bits exponent, 23 bits mantissa
        return True
    elif type_to_cast == "float64":  # Double precision float: sign bit, 11 bits exponent, 52 bits mantissa
        return True
    elif type_to_cast == "str":  # let cast numbers to str
        return True
    else:
        return "Unknown type"


def is_even(number):

    return number % 2 == 0
