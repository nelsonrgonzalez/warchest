import numpy as np
from clf_adaline_gd import AdalineGD
from sklearn.metrics import accuracy_score


def AutoClfAdalineGD(X_train,
                     X_test,
                     y_train,
                     y_test,
                     n_iter,
                     eta0):

    # Instantiate AdalineGD
    adagd = AdalineGD(n_iter=n_iter, eta=eta0)
    # Fit
    adagd.fit(X_train, y_train)
    # Predict
    y_pred = adagd.predict(X_test)
    # Results
    misc_samples = (y_test != y_pred).sum()
    misc_error = np.asscalar((y_test != y_pred).sum()/y_test.shape)
    accuracy = accuracy_score(y_test, y_pred)
    training_accuracy = adagd.score(X_train, y_train)
    test_accuracy = adagd.score(X_test, y_test)

    print("\nResults: Adaline GD Classifier")
    print("-----------------------------------------")
    print('Misclassified samples: %d' % misc_samples)
    print('Misclassified error: %.2f' % misc_error)
    print('Accuracy: %.5f' % accuracy)
    print('\nTraining accuracy: %.5f' % training_accuracy)
    print('Test accuracy: %.5f' % test_accuracy)
    if (training_accuracy > test_accuracy):
        print("Possible overfitting.")

    return adagd
