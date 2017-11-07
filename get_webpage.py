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

from urllib.request import urlopen


def GetWebpage(url, output="s"):
    response = urlopen('http://python.org/')
    if (output == "s"):
        # response.read() returns a bytes-like object so use .decode() to
        # convert to a unicode string
        html = response.read().decode("utf-8")
    if (output == "b"):
        # default return of bytes-like object
        html = response.read()

    return html
