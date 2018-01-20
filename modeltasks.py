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


class ModelTask():

    def __init__(self):

        pass

    def update_model_override_algorithms(self):

        qry_del = 'DELETE FROM ModelOverrideAlgorithms'
        exec_qry(qry_del)

        qry_sel = 'SELECT * FROM ModelDefaultAlgorithms ORDER BY AlgorithmID'
        algorithms = exec_qry(qry_sel)
        lst = []
        for row in algorithms:
            lst.append(list([row[0], row[1], row[2], row[3], row[4]]))

        for row in lst:
            qry_ins = "INSERT INTO ModelOverrideAlgorithms (" \
                "AlgorithmID, AlgorithmDesc, " \
                "AlgorithmTypeID, NeedsScaling, IsSelected) " \
                "VALUES (?, ?, ?, ?, ?)"
            parameters = (row[0], row[1], row[2], row[3], row[4])
            exec_insert_qry(qry_ins, parameters)

    def update_model_override_algorithm_params(self):

        qry_del = 'DELETE FROM ModelOverrideAlgorithmParams'
        exec_qry(qry_del)

        qry_sel = 'SELECT * FROM ModelDefaultAlgorithmParams ORDER BY AlgorithmID'
        algorithms = exec_qry(qry_sel)
        lst = []
        for row in algorithms:
            lst.append(list([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]]))

        for row in lst:
            qry_ins = "INSERT INTO ModelOverrideAlgorithmParams (" \
                "AlgorithmParamID, AlgorithmID, ParamName, " \
                "ParamType, DefaultsTo, DependsOn, IsOptional, IsSelected) " \
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            parameters = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            exec_insert_qry(qry_ins, parameters)

    def update_model_overrides(self):

        qry_del = 'DELETE FROM ModelOverrides'
        exec_qry(qry_del)

        qry_sel = 'SELECT * FROM ModelDefaults'
        defaults = exec_qry(qry_sel)
        lst = []
        for row in defaults:
            lst.append(list([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]]))

        for row in lst:
            qry_ins = "INSERT INTO ModelOverrides (" \
                "ModelOverrideID, ModelOverrideName, " \
                "ModelOverrideText1, ModelOverrideText2, " \
                "ModelOverrideInt1, ModelOverrideInt2, " \
                "ModelOverrideFloat1, ModelOverrideFloat2) " \
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            parameters = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            exec_insert_qry(qry_ins, parameters)

    def get_selected_classifiers(self):

        qry = 'SELECT AlgorithmID FROM ModelOverrideAlgorithms WHERE IsSelected=? AND AlgorithmTypeID=1'
        parameters = ('Yes',)
        cursor = exec_qry(qry, parameters)
        lst = []
        for row in cursor:
            lst.append(row[0])
        return lst

    def get_selected_params(self):

        qry = 'SELECT * FROM ModelOverrideAlgorithmParams WHERE IsSelected=?'
        parameters = (1,)
        cursor = exec_qry(qry, parameters)
        lst = []
        for row in cursor:
            print(row[1])
            lst.append(list([row[1], row[2], row[3], row[4], row[6]]))
        return lst

    def get_selected_train_test_splits(self):

        qry = 'SELECT * FROM ModelOverrides WHERE ModelOverrideName=?'
        parameters = ('train_and_test_split',)
        cursor = exec_qry(qry, parameters)

        for row in cursor:
            return(row[4], row[5], row[6], row[7])

    def get_selected_scaling(self):

        qry = 'SELECT * FROM ModelOverrides WHERE ModelOverrideName=?'
        parameters = ('scaling',)
        cursor = exec_qry(qry, parameters)

        for row in cursor:
            return row[4]

    def add_simple_set_entry(self,
                             session,
                             simple_set_id,
                             algorithm_id,
                             parameters,
                             misclassified_samples,
                             misclassified_error,
                             skl_accuracy_score,
                             training_accuracy,
                             test_accuracy,
                             overfitting):

        qry = "INSERT INTO SimpleSets (" \
            "SessionID, SimpleSetID, DateCreated, AlgorithmID, " \
            "Parameters, MisclassifiedSamples, MisclassifiedError, " \
            "SKLAccuracyScore, TrainingAccuracy, TestAccuracy, " \
            "Overfitting) " \
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        parameters = (session, simple_set_id, datetime.now(),
                      algorithm_id, parameters, misclassified_samples,
                      misclassified_error, skl_accuracy_score,
                      training_accuracy, test_accuracy, overfitting)

        return exec_insert_qry(qry, parameters)

    def get_next_available_simple_set_number(self):

        qry = 'SELECT MAX(SimpleSetID) FROM SimpleSets'
        cursor = exec_qry(qry)

        for row in cursor:
            return row[0]+1

    def get_max_simple_set_number(self):

        qry = 'SELECT MAX(SimpleSetID) FROM SimpleSets'
        cursor = exec_qry(qry)

        for row in cursor:
            return row[0]

    def get_simple_set_by_simple_set_id(self, simple_set_id):

        qry = 'SELECT SimpleSets.ID, ' \
            'SimpleSets.SessionID, ' \
            'SimpleSets.SimpleSetID, ' \
            'SimpleSets.DateCreated, ' \
            'Algorithms.AlgorithmDesc, ' \
            'SimpleSets.Parameters, ' \
            'SimpleSets.MisclassifiedSamples, ' \
            'SimpleSets.MisclassifiedError, ' \
            'SimpleSets.SKLAccuracyScore, ' \
            'SimpleSets.TrainingAccuracy, ' \
            'SimpleSets.TestAccuracy, ' \
            'SimpleSets.Overfitting ' \
            'FROM SimpleSets ' \
            'INNER JOIN Algorithms ' \
            'ON SimpleSets.AlgorithmID = Algorithms.AlgorithmID ' \
            'WHERE SimpleSets.SimpleSetID=? ' \
            'ORDER BY SimpleSets.ID DESC'
        parameters = (simple_set_id,)
        cursor = exec_qry(qry, parameters)
        return cursor.fetchall()
