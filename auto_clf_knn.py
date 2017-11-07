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
from sklearn.neighbors import KNeighborsClassifier
from feat_sel_sbs import SBS
from sklearn.metrics import accuracy_score


def AutoClfKNN(X_train,
               X_test,
               y_train,
               y_test,
               n_neighbors,
               p,
               metric):

    # Instantiate K-nearest Neighbors
    knn = KNeighborsClassifier(n_neighbors=n_neighbors,
                               p=p,
                               metric=metric)
    # Fit
    knn.fit(X_train, y_train)
    # Predict
    y_pred = knn.predict(X_test)

    # Results
    misc_samples = (y_test != y_pred).sum()
    misc_error = np.asscalar((y_test != y_pred).sum()/y_test.shape)
    accuracy = accuracy_score(y_test, y_pred)
    training_accuracy = knn.score(X_train, y_train)
    test_accuracy = knn.score(X_test, y_test)

    print("\nResults: K-nearest Neighbors Classifier")
    print("-----------------------------------------")
    print('Misclassified samples: %d' % misc_samples)
    print('Misclassified error: %.2f' % misc_error)
    print('Accuracy: %.5f' % accuracy)
    print('\nTraining accuracy: %.5f' % training_accuracy)
    print('Test accuracy: %.5f' % test_accuracy)
    if (training_accuracy > test_accuracy):
        print("Possible overfitting.")

    return knn
