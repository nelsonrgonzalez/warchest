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

from toolbox import exec_qry, is_float_series_integer, is_integer_series_natural
from datetime import datetime
from global_config import g


class ColumnInsight():

    def __init__(self, col_values, column_tab_dict):

        self.col_values = col_values
        self.column_tab_dict = column_tab_dict

        # column identity
        self.column_index = int(self.
                                column_tab_dict['selected_column_entry'][0])
        self.column_name = self. \
            column_tab_dict['selected_column_name_entry'][0]

        # feature information
        self.feature_type = self.column_tab_dict['feature_type_entry'][0]
        self.dtype = str(self.column_tab_dict['dtype_entry'][0])

        # memory usage
        self.bytes_in_data_entry = self. \
            column_tab_dict['bytes_in_data_entry'][0]
        self.bytes_in_col_index_entry = self. \
            column_tab_dict['bytes_in_col_index_entry'][0]
        self.memusage_of_col_without_index_entry = self. \
            column_tab_dict['memusage_of_col_without_index_entry'][0]
        self.memusage_of_col_with_index_entry = self. \
            column_tab_dict['memusage_of_col_with_index_entry'][0]
        self.deep_memusage_of_col_with_index_entry = self. \
            column_tab_dict['deep_memusage_of_col_with_index_entry'][0]
        self.getsizeof_col_entry = self. \
            column_tab_dict['getsizeof_col_entry'][0]

    def get_insights(self):

        qry = 'SELECT * FROM Insights'
        return exec_qry(qry)

    def reset_insights(self):

        # remove all records in Insights table
        table_name = 'Insights'
        qry = "DELETE FROM {tbl}".format(tbl=table_name)
        exec_qry(qry)

        # reset autonumber in Insights table
        sqlite_table_name = 'sqlite_sequence'
        where_column1 = 'name'
        update_column_1 = 'seq'

        qry = "UPDATE {tbl} SET {col}=? WHERE {cond}=?".\
            format(col=update_column_1,
                   tbl=sqlite_table_name,
                   cond=where_column1)
        parameters = (0, table_name)
        return exec_qry(qry, parameters)

    def missing_values(self):

        if self.col_values.isnull().sum() > 0:

            self._add_insight(column_index=self.column_index,
                              column_name=self.column_name,
                              insight_text='Missing values found in column (' +
                              self.column_name + '), index (' +
                              str(self.column_index) + ').',
                              insight_priority='High',
                              language_id=g.localized_lang)
            return True
        else:
            return False

    def memory_usage(self):

        # for all floats
        if (self.dtype == 'float64' or self.dtype == 'float32' or
                self.dtype == 'float16'):

            # check if column has all integer numbers
            if is_float_series_integer(self.col_values) is True:
                # recommend to cast to some form of int
                self._add_insight(column_index=self.column_index,
                                  column_name=self.column_name,
                                  insight_text='Try converting column (' +
                                  self.column_name + '), index (' +
                                  str(self.column_index) + ') to integer.',
                                  insight_priority='Medium',
                                  language_id=g.localized_lang)
            else:
                if (self.dtype == 'float64' or self.dtype == 'float32'):
                    # recommend to cast to smaller precision float
                    self._add_insight(column_index=self.column_index,
                                      column_name=self.column_name,
                                      insight_text='Try converting column (' +
                                      self.column_name + '), index (' +
                                      str(self.column_index) + ') to a ' +
                                      'smaller precision float.',
                                      insight_priority='Medium',
                                      language_id=g.localized_lang)

        # for all signed integers
        if (self.dtype == 'int64' or self.dtype == 'int32' or
                self.dtype == 'int16' or self.dtype == 'int8'):

            # check if column only has positive numbers
            if is_integer_series_natural(self.col_values) is True:
                # recommend to cast to unsigned integers
                self._add_insight(column_index=self.column_index,
                                  column_name=self.column_name,
                                  insight_text='Try converting column (' +
                                  self.column_name + '), index (' +
                                  str(self.column_index) + ') to unsigned ' +
                                  'integer.',
                                  insight_priority='Medium',
                                  language_id=g.localized_lang)
            else:
                if (self.dtype == 'int64' or self.dtype == 'int32' or
                        self.dtype == 'int16'):
                    # recommend to cast to smaller integer
                    self._add_insight(column_index=self.column_index,
                                      column_name=self.column_name,
                                      insight_text='Try converting column (' +
                                      self.column_name + '), index (' +
                                      str(self.column_index) + ') to a ' +
                                      'smaller integer.',
                                      insight_priority='Medium',
                                      language_id=g.localized_lang)

        # for all unsigned integers
        if (self.dtype == 'uint64' or self.dtype == 'uint32' or
                self.dtype == 'uint16'):

            # recommend to cast to smaller unsigned integer
            self._add_insight(column_index=self.column_index,
                              column_name=self.column_name,
                              insight_text='Try converting column (' +
                              self.column_name + '), index (' +
                              str(self.column_index) + ') to a ' +
                              'smaller unsigned integer.',
                              insight_priority='Medium',
                              language_id=g.localized_lang)
        return

    def _add_insight(self,
                     column_index=0,
                     column_name='',
                     insight_text='',
                     insight_priority='',
                     language_id=1):

        # fields to insert into
        table_name = 'Insights'
        col_index = 'ColumnIndex'
        col_name = 'ColumnName'
        col_insight_text = 'InsightText'
        col_insight_priority = 'InsightPriority'
        col_date_created = 'DateCreated'
        col_language_id = 'LanguageID'

        qry = "INSERT INTO {tbl} ({col1}, {col2}, {col3}, {col4}, {col5}, {col6}) VALUES (?, ?, ?, ?, ?, ?)".\
            format(tbl=table_name, col1=col_index, col2=col_name,
                   col3=col_insight_text, col4=col_insight_priority,
                   col5=col_date_created, col6=col_language_id)
        parameters = (column_index, column_name, insight_text,
                      insight_priority, datetime.now(), language_id)

        return exec_qry(qry, parameters)
