import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score


def AutoClfLogisticRegression(X_train,
                              X_test,
                              y_train,
                              y_test,
                              C,
                              penalty,
                              random_state):

    # Instantiate Logistic Regression
    lr = LogisticRegression(C=C, penalty=penalty, random_state=random_state)
    # Fit
    lr.fit(X_train, y_train)
    # Predict
    y_pred = lr.predict(X_test)

    # Probability of one item
    # print(lr.predict_proba(X_test[0,:].reshape(1, -1)))

    # Results
    misc_samples = (y_test != y_pred).sum()
    misc_error = np.asscalar((y_test != y_pred).sum()/y_test.shape)
    accuracy = accuracy_score(y_test, y_pred)
    training_accuracy = lr.score(X_train, y_train)
    test_accuracy = lr.score(X_test, y_test)
    # lr.intercept_
    # lr.coef_
    # lr.n_iter_

    print("\nResults: Logistic Regression Classifier")
    print("-----------------------------------------")
    print('Misclassified samples: %d' % misc_samples)
    print('Misclassified error: %.2f' % misc_error)
    print('Accuracy: %.5f' % accuracy)
    print('\nTraining accuracy: %.5f' % training_accuracy)
    print('Test accuracy: %.5f' % test_accuracy)
    if (training_accuracy > test_accuracy):
        print("Possible overfitting.")

    return lr
