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

from toolbox import exec_qry, exec_insert_qry
from datetime import datetime


class Session():

    def __init__(self):

        pass

    def get_current_session(self):

        qry = 'SELECT SessionID FROM CurrentSession'

        cursor = exec_qry(qry)

        for row in cursor:
            return row[0]

    def add_session(self, filename):

        col_session_desc = 'SessionDesc'
        col_date_created = 'DateCreated'

        qry_ins = "INSERT INTO Sessions ({col1}, {col2}) VALUES (?, ?)".\
            format(col1=col_session_desc,
                   col2=col_date_created)
        parameters = (filename, datetime.now())

        new_session_id = exec_insert_qry(qry_ins, parameters)

        qry_upd = 'UPDATE CurrentSession SET SessionID=?'
        parameters = (new_session_id,)
        exec_qry(qry_upd, parameters)

        return new_session_id
