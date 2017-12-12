from toolbox import exec_qry, exec_insert_qry
from datetime import datetime
import pandas as pd
from modeloptions import ModelOption


class Transformation():

    def __init__(self):

        pass
#        self.transformation = ''
#        self.transformation_id = 0

    def _get_transformation_id(self, transformation):

        qry = 'SELECT TransformationID FROM Transformations WHERE TransformationDesc=?'
        parameters = (transformation,)

        cursor = exec_qry(qry, parameters)

        for row in cursor:
            return row[0]

#    def _get_transformation(self):
#
#        qry = 'SELECT TransformationDesc FROM Transformations WHERE TransformationID=?'
#        parameters = (self.transformation_id,)
#
#        cursor = exec_qry(qry, parameters)
#
#        for row in cursor:
#            return row[0]

    def get_transformations_by_session(self, session):

        qry = 'SELECT TransformationsLog.TransformationLogID, ' \
            'TransformationsLog.SessionID, ' \
            'Sessions.SessionDesc, ' \
            'TransformationsLog.ColumnIndex, ' \
            'TransformationsLog.ColumnName, ' \
            'TransformationsLog.TransformationID, ' \
            'Transformations.TransformationDesc, ' \
            'TransformationsLog.DateCreated, ' \
            'TransformationsLog.TransformationLogDesc, ' \
            'TransformationsLog.IsReplicate, ' \
            'TransformationsLog.Option1, ' \
            'TransformationsLog.Option2, ' \
            'TransformationsLog.Option3 ' \
            'FROM TransformationsLog ' \
            'INNER JOIN Sessions ' \
            'ON TransformationsLog.SessionID = Sessions.SessionID ' \
            'INNER JOIN Transformations ' \
            'ON TransformationsLog.TransformationID = Transformations.TransformationID ' \
            'WHERE TransformationsLog.SessionID=?'
        parameters = (session,)
        cursor = exec_qry(qry, parameters)
        return cursor.fetchall()

    def delete_transformations_by_session(self, session):

        qry = 'DELETE FROM TransformationsLog WHERE SessionID=?'
        parameters = (session,)
        exec_qry(qry, parameters)

    def add_transformation(self,
                           session,
                           index,
                           name,
                           transformation,
                           **kwargs):

        #self.transformation = transformation
        transformation_id = self._get_transformation_id(transformation)

        self.qry_ins = "INSERT INTO TransformationsLog (" \
            "SessionID, ColumnIndex, ColumnName, TransformationID, " \
            "DateCreated, TransformationLogDesc, IsReplicate) " \
            "VALUES (?, ?, ?, ?, ?, ?, ?)"
        self.parameters = (session, index, name, transformation_id,
                           datetime.now(), '', 'Yes')

        qry_hd = "INSERT INTO TransformationsLog (" \
            "SessionID, ColumnIndex, ColumnName, TransformationID, " \
            "DateCreated, TransformationLogDesc, IsReplicate"

        if transformation == 'setColumnType':
            for key, value in dict(**kwargs).items():
                if key == 'option1':
                    qry_kwargs = ", Option1) "
                    val_kwargs = "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                    self.qry_ins = qry_hd + qry_kwargs + val_kwargs
                    desc = 'Cast column (' + name + ') at index (' + \
                        str(index) + ') to ' + value + ' data type.'
                    self.parameters = (session, index, name,
                                       transformation_id,
                                       datetime.now(), desc, 'Yes', value)

        if transformation == 'createCategorical':
            qry_kwargs = ", Option1, Option2, Option3) "
            val_kwargs = "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            self.qry_ins = qry_hd + qry_kwargs + val_kwargs
            for key, value in dict(**kwargs).items():
                if key == 'option1':
                    trx_type = value
                if key == 'option2':
                    new_col_flag = value
                if key == 'option3':
                    old_col = value
            if trx_type == 'convert':
                if new_col_flag == 'new_col':
                    desc = 'Add new integer codes column (' + name + ') ' + \
                        'based on column (' + old_col + ') at index (' + \
                        str(index) + ') from categorical conversion.'
                else:
                    desc = 'Categorical conversion of column (' + \
                        name + ') at index (' + \
                        str(index) + ') to integer codes.'
                self.parameters = (session, index, name,
                                   transformation_id,
                                   datetime.now(), desc, 'Yes',
                                   trx_type, new_col_flag, old_col)
#dummies
#bins
#encode
#ordinal




        return exec_insert_qry(self.qry_ins, self.parameters)

    def toggle_selected(self, flag, trans_id):

        qry = 'UPDATE TransformationsLog SET IsReplicate=? ' \
            'WHERE TransformationLogID=?'
        parameters = (flag, trans_id)
        exec_qry(qry, parameters)

    def flag_all(self, session_id):

        qry = 'UPDATE TransformationsLog SET IsReplicate=? ' \
            'WHERE SessionID=?'
        parameters = ('Yes', session_id)
        exec_qry(qry, parameters)

    def unflag_all(self, session_id):

        qry = 'UPDATE TransformationsLog SET IsReplicate=? ' \
            'WHERE SessionID=?'
        parameters = ('No', session_id)
        exec_qry(qry, parameters)

    def replicate(self, lst, df):

        print(lst)
        for trans in lst:

            index = trans.get('ColumnIndex')
            name = trans.get('ColumnName')
            transformation = trans.get('TransformationDesc')

            if transformation == 'setColumnType':
                dtype = trans.get('Option1')
                col = df.columns[index]
                df[col] = df[col].astype(dtype)

            if transformation == 'createCategorical':
                option1 = trans.get('Option1')
                option2 = trans.get('Option2')
                if option1 == 'convert':
                    col = df.columns[index]
                    df[name] = pd.Categorical(df[col]).codes
                    if option2 == 'new_col':
                        self.add_col_to_model_columns(1)

    def update_model_option_available_to_model(self, var):

        modelopt = ModelOption()
        modelopt.update_model_option('available_to_model_dict', var)

    def update_model_option_class_label_status(self, var):

        modelopt = ModelOption()
        modelopt.update_model_option('class_label_status_dict', var)

    def update_model_option_nominal_ordinal(self, var):

        modelopt = ModelOption()
        modelopt.update_model_option('nominal_ordinal_dict', var)

    def get_model_option_x(self, option):

        modelopt = ModelOption()
        return {int(k): v for k, v in modelopt.get_model_option(option).items()}

    def add_col_to_model_columns(self, number_of_cols):

        for i in range(number_of_cols):

            self.available_to_model = self. \
                get_model_option_x('available_to_model_dict')
            self.class_label_status = self. \
                get_model_option_x('class_label_status_dict')
            self.nominal_ordinal = self.get_model_option_x('nominal_ordinal_dict')

            self.available_to_model[max(list(self.available_to_model)) + 1] = 'No'
            self.class_label_status[max(list(self.class_label_status)) + 1] = 'No'
            self.nominal_ordinal[max(list(self.nominal_ordinal)) + 1] = 'nominal'

            self.update_model_option_available_to_model(self.available_to_model)
            self.update_model_option_class_label_status(self.class_label_status)
            self.update_model_option_nominal_ordinal(self.nominal_ordinal)

#{'TransformationLogID': 105, 'SessionID': 130, 'SessionDesc': 'iris.csv',
# 'ColumnIndex': 0, 'ColumnName': '0', 'TransformationID': 1,
# 'TransformationDesc': 'setColumnType',
# 'DateCreated': '2017-11-15 22:03:53.821886',
# 'TransformationLogDesc': 'Cast column (0), index (0) to (float16).',
# 'IsReplicate': 'Yes', 'DType': 'float16'}

#        for k, v in [(k, v) for x in lst for (k, v) in x.items()]:
#            print(k, v)
#        print([(k, v) for x in lst for (k, v) in x.items()])
