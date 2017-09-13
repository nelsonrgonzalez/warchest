import numpy as np
from sklearn.linear_model import Perceptron
from sklearn.metrics import accuracy_score


def AutoClfPerceptron(X_train,
                      X_test,
                      y_train,
                      y_test,
                      n_iter,
                      eta0,
                      random_state):

    # Instantiate Perceptron
    ppn = Perceptron(n_iter=n_iter, eta0=eta0, random_state=random_state)
    # Fit
    ppn.fit(X_train, y_train)
    # Predict
    y_pred = ppn.predict(X_test)
    # Results
    misc_samples = (y_test != y_pred).sum()
    misc_error = np.asscalar((y_test != y_pred).sum()/y_test.shape)
    accuracy = accuracy_score(y_test, y_pred)
    training_accuracy = ppn.score(X_train, y_train)
    test_accuracy = ppn.score(X_test, y_test)
    # lr.intercept_
    # lr.coef_
    # lr.n_iter_

    print("\nResults: Perceptron Classifier")
    print("-----------------------------------------")
    print('Misclassified samples: %d' % misc_samples)
    print('Misclassified error: %.2f' % misc_error)
    print('Accuracy: %.5f' % accuracy)
    print('\nTraining accuracy: %.5f' % training_accuracy)
    print('Test accuracy: %.5f' % test_accuracy)
    if (training_accuracy > test_accuracy):
        print("Possible overfitting.")

    return ppn
