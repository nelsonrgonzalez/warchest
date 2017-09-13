import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


def AutoClfRandomForest(X_train,
                        X_test,
                        y_train,
                        y_test,
                        criterion,
                        n_estimators,
                        random_state):

    # Instantiate Random Forest
    forest = RandomForestClassifier(criterion=criterion,
                                    n_estimators=n_estimators,
                                    random_state=random_state)
    # Fit
    forest.fit(X_train, y_train)
    # Predict
    y_pred = forest.predict(X_test)

    # Results
    misc_samples = (y_test != y_pred).sum()
    misc_error = np.asscalar((y_test != y_pred).sum()/y_test.shape)
    accuracy = accuracy_score(y_test, y_pred)
    training_accuracy = forest.score(X_train, y_train)
    test_accuracy = forest.score(X_test, y_test)

    print("\nResults: Random Forest Classifier")
    print("-----------------------------------------")
    print('Misclassified samples: %d' % misc_samples)
    print('Misclassified error: %.2f' % misc_error)
    print('Accuracy: %.5f' % accuracy)
    print('\nTraining accuracy: %.5f' % training_accuracy)
    print('Test accuracy: %.5f' % test_accuracy)
    if (training_accuracy > test_accuracy):
        print("Possible overfitting.")

    return forest
