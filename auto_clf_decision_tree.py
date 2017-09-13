import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score


def AutoClfDecisionTree(X_train,
                        X_test,
                        y_train,
                        y_test,
                        criterion,
                        max_depth,
                        random_state):

    # Instantiate Decision Tree
    tree = DecisionTreeClassifier(criterion=criterion, max_depth=max_depth,
                                  random_state=random_state)
    # Fit
    tree.fit(X_train, y_train)
    # Predict
    y_pred = tree.predict(X_test)

    # Results
    misc_samples = (y_test != y_pred).sum()
    misc_error = np.asscalar((y_test != y_pred).sum()/y_test.shape)
    accuracy = accuracy_score(y_test, y_pred)
    training_accuracy = tree.score(X_train, y_train)
    test_accuracy = tree.score(X_test, y_test)

    print("\nResults: Decision Tree Classifier")
    print("-----------------------------------------")
    print('Misclassified samples: %d' % misc_samples)
    print('Misclassified error: %.2f' % misc_error)
    print('Accuracy: %.5f' % accuracy)
    print('\nTraining accuracy: %.5f' % training_accuracy)
    print('Test accuracy: %.5f' % test_accuracy)
    if (training_accuracy > test_accuracy):
        print("Possible overfitting.")

    return tree
