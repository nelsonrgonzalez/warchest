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

import numpy as np
from sklearn.linear_model import Perceptron
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
from modeltasks import ModelTask
import json


def process_clf(clf, x_train, x_test, y_train, y_test, session_id, simple_set_id, algorithm_id, **kwargs):

    clf.fit(x_train, y_train)
    y_pred = clf.predict(x_test)

    misc_samples = int((y_test != y_pred).sum())
    misc_error = np.asscalar((y_test != y_pred).sum()/y_test.shape)
    accuracy = accuracy_score(y_test, y_pred)
    training_accuracy = clf.score(x_train, y_train)
    test_accuracy = clf.score(x_test, y_test)
    if (training_accuracy > test_accuracy):
        overfitting = "Possible"
    else:
        overfitting = ""

    model_task = ModelTask()
    model_task.add_simple_set_entry(session=session_id,
                                    simple_set_id=simple_set_id,
                                    algorithm_id=algorithm_id,
                                    parameters=json.dumps(kwargs),
                                    misclassified_samples=misc_samples,
                                    misclassified_error=misc_error,
                                    skl_accuracy_score=accuracy,
                                    training_accuracy=training_accuracy,
                                    test_accuracy=test_accuracy,
                                    overfitting=overfitting)

    print("\nResults:")
    print("-----------------------------------------")
    print('Algorithm: %d' % algorithm_id)
    print('Misclassified samples: %d' % misc_samples)
    print('Misclassified error: %.2f' % misc_error)
    print('Accuracy: %.5f' % accuracy)
    print('\nTraining accuracy: %.5f' % training_accuracy)
    print('Test accuracy: %.5f' % test_accuracy)
    if (training_accuracy > test_accuracy):
        print("Possible overfitting.")


def clf_sklearn_perceptron(x_train, x_test, y_train, y_test, session_id,
                           simple_set_id, algorithm_id, **kwargs):

    clf = Perceptron(**kwargs)
    process_clf(clf, x_train, x_test, y_train, y_test, session_id, simple_set_id, algorithm_id, **kwargs)
    return clf

def clf_sklearn_logistic_regression(x_train, x_test, y_train, y_test,
                                    session_id, simple_set_id, algorithm_id, **kwargs):

    clf = LogisticRegression(**kwargs)
    process_clf(clf, x_train, x_test, y_train, y_test, session_id, simple_set_id, algorithm_id, **kwargs)
    return clf


def clf_sklearn_linear_svm(x_train, x_test, y_train, y_test, session_id,
                           simple_set_id, algorithm_id, **kwargs):

    clf = LinearSVC(**kwargs)
    process_clf(clf, x_train, x_test, y_train, y_test, session_id, simple_set_id, algorithm_id, **kwargs)
    return clf


def clf_sklearn_kernel_svm(x_train, x_test, y_train, y_test, session_id,
                           simple_set_id, algorithm_id, **kwargs):

    clf = SVC(**kwargs)
    process_clf(clf, x_train, x_test, y_train, y_test, session_id, simple_set_id, algorithm_id, **kwargs)
    return clf


def clf_sklearn_decision_tree(x_train, x_test, y_train, y_test, session_id,
                              simple_set_id, algorithm_id, **kwargs):

    clf = DecisionTreeClassifier(**kwargs)
    process_clf(clf, x_train, x_test, y_train, y_test, session_id, simple_set_id, algorithm_id, **kwargs)
    return clf


def clf_sklearn_random_forest(x_train, x_test, y_train, y_test, session_id,
                              simple_set_id, algorithm_id, **kwargs):

    clf = RandomForestClassifier(**kwargs)
    process_clf(clf, x_train, x_test, y_train, y_test, session_id, simple_set_id, algorithm_id, **kwargs)
    return clf


def clf_sklearn_k_neighbors(x_train, x_test, y_train, y_test, session_id,
                            simple_set_id, algorithm_id, **kwargs):

    clf = KNeighborsClassifier(**kwargs)
    process_clf(clf, x_train, x_test, y_train, y_test, session_id, simple_set_id, algorithm_id, **kwargs)
    return clf
