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

from toolbox import exec_qry
import json


class ModelOption():

    def __init__(self):

        pass

    def get_model_option(self, option):

        qry = 'SELECT ModelOptionDesc FROM ModelOptions WHERE ModelOptionName=?'
        parameters = (option,)
        cursor = exec_qry(qry, parameters)

        for row in cursor:
            return json.loads(row[0])

    def update_model_option(self, option, newvalue):

        qry = 'UPDATE ModelOptions SET ModelOptionDesc=? WHERE ModelOptionName=?'
        parameters = (json.dumps(newvalue), option)
        exec_qry(qry, parameters)
