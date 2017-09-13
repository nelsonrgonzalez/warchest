import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from plot_decision_regions import plot_decision_regions
from auto_clf_perceptron import AutoClfPerceptron
from auto_clf_adaline_gd import AutoClfAdalineGD
from auto_clf_adaline_sgd import AutoClfAdalineSGD
from auto_clf_logistic_regression import AutoClfLogisticRegression
from auto_clf_linear_svm import AutoClfLinearSVM
from auto_clf_kernel_svm import AutoClfKernelSVM
from auto_clf_decision_tree import AutoClfDecisionTree
from auto_clf_random_forest import AutoClfRandomForest
from auto_clf_knn import AutoClfKNN
from global_config import g


def Automator(classifier,
              X_train,
              X_test,
              y_train,
              y_test,
              X_combined,
              y_combined,
              n_iter=15,
              eta0=0.1,
              C=1000.0,
              penalty='l2',
              kernel='linear',
              gamma=0.2,
              criterion='entropy',
              max_depth=3,
              n_estimators=10,
              n_neighbors=5,
              p=2,
              metric='minkowski',
              random_state=0):

    if (classifier == "ClfPerceptron"):
        # Fit with Perceptron
        ppn = AutoClfPerceptron(X_train=X_train,
                                X_test=X_test,
                                y_train=y_train,
                                y_test=y_test,
                                n_iter=n_iter,
                                eta0=eta0,
                                random_state=random_state)

        if (g.decision_regions is True):
            # Plot Perceptron decision regions
            plot_decision_regions(X=X_combined, y=y_combined,
                                  classifier=ppn, test_idx=range(105, 150))
            plt.xlabel('petal length [standardized]')
            plt.ylabel('petal width [standardized]')
            plt.title('Perceptron')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()

    if (classifier == "ClfAdalineGD"):
         # Fit with AdalineGD
        adagd = AutoClfAdalineGD(X_train=X_train,
                                 X_test=X_test,
                                 y_train=y_train,
                                 y_test=y_test,
                                 n_iter=n_iter,
                                 eta0=eta0)

        if (g.decision_regions is True):
            # Plot AdalineGD decision regions
            plot_decision_regions(X=X_combined, y=y_combined,
                                  classifier=adagd, test_idx=range(105, 150))
            plt.xlabel('petal length [standardized]')
            plt.ylabel('petal width [standardized]')
            plt.title('AdalineGD')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()

    if (classifier == "ClfAdalineSGD"):
        # Fit with AdalineSGD
        adasgd = AutoClfAdalineSGD(X_train=X_train,
                                   X_test=X_test,
                                   y_train=y_train,
                                   y_test=y_test,
                                   n_iter=n_iter,
                                   eta0=eta0,
                                   random_state=random_state)

        if (g.decision_regions is True):
            # Plot AdalineGD decision regions
            plot_decision_regions(X=X_combined, y=y_combined,
                                  classifier=adasgd, test_idx=range(105, 150))
            plt.xlabel('petal length [standardized]')
            plt.ylabel('petal width [standardized]')
            plt.title('AdalineSGD')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()

    if (classifier == "ClfLogisticRegression"):
        # Fit with Logistic Regression
        lr = AutoClfLogisticRegression(X_train=X_train,
                                       X_test=X_test,
                                       y_train=y_train,
                                       y_test=y_test,
                                       C=C,
                                       penalty=penalty,
                                       random_state=random_state)

        if (g.decision_regions is True):
            # Plot Logistic Regression decision regions
            plot_decision_regions(X=X_combined, y=y_combined,
                                  classifier=lr, test_idx=range(105, 150))
            plt.xlabel('petal length [standardized]')
            plt.ylabel('petal width [standardized]')
            plt.title('Logistic Regression')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()

    if (classifier == "ClfLinearSVM"):
        # Fit with Linear Support Vector Machines
        lsvm = AutoClfLinearSVM(X_train=X_train,
                                X_test=X_test,
                                y_train=y_train,
                                y_test=y_test,
                                kernel=kernel,
                                C=C,
                                random_state=random_state)

        if (g.decision_regions is True):
            # Plot Linear Support Vector Machines decision regions
            plot_decision_regions(X=X_combined, y=y_combined,
                                  classifier=lsvm, test_idx=range(105, 150))
            plt.xlabel('petal length [standardized]')
            plt.ylabel('petal width [standardized]')
            plt.title('Linear Support Vector Machines')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()

    if (classifier == "ClfKernelSVM"):
        # Fit with Kernel Support Vector Machines
        ksvm = AutoClfKernelSVM(X_train=X_train,
                                X_test=X_test,
                                y_train=y_train,
                                y_test=y_test,
                                kernel=kernel,
                                gamma=gamma,
                                C=C,
                                random_state=random_state)

        if (g.decision_regions is True):
            # Plot Kernel Support Vector Machines decision regions
            plot_decision_regions(X=X_combined, y=y_combined,
                                  classifier=ksvm, test_idx=range(105, 150))
            plt.xlabel('petal length [standardized]')
            plt.ylabel('petal width [standardized]')
            plt.title('Kernel Support Vector Machines')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()

    if (classifier == "ClfDecisionTree"):
        # Fit with Decision Tree
        tree = AutoClfDecisionTree(X_train=X_train,
                                   X_test=X_test,
                                   y_train=y_train,
                                   y_test=y_test,
                                   criterion=criterion,
                                   max_depth=max_depth,
                                   random_state=random_state)

        if (g.decision_regions is True):
            # Plot Decision Tree decision regions
            plot_decision_regions(X=X_combined, y=y_combined,
                                  classifier=tree, test_idx=range(105, 150))
            plt.xlabel('petal length [cm]')
            plt.ylabel('petal width [cm]')
            plt.title('Decision Tree')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()

    if (classifier == "ClfRandomForest"):
        # Fit with Random Forest
        tree = AutoClfRandomForest(X_train=X_train,
                                   X_test=X_test,
                                   y_train=y_train,
                                   y_test=y_test,
                                   criterion=criterion,
                                   n_estimators=n_estimators,
                                   random_state=random_state)

        if (g.decision_regions is True):
            # Plot Random Forest decision regions
            plot_decision_regions(X=X_combined, y=y_combined,
                                  classifier=tree, test_idx=range(105, 150))
            plt.xlabel('petal length [cm]')
            plt.ylabel('petal width [cm]')
            plt.title('Random Forest')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()

    if (classifier == "ClfKNN"):
        # Fit with K-nearest Neighbors
        knn = AutoClfKNN(X_train=X_train,
                          X_test=X_test,
                          y_train=y_train,
                          y_test=y_test,
                          n_neighbors=n_neighbors,
                          p=p,
                          metric=metric)

        if (g.decision_regions is True):
            # Plot K-nearest Neighbors decision regions
            plot_decision_regions(X=X_combined, y=y_combined,
                                  classifier=knn, test_idx=range(105, 150))
            plt.xlabel('petal length [standardized]')
            plt.ylabel('petal width [standardized]')
            plt.title('K-nearest Neighbors')
            plt.legend(loc='upper left')
            plt.tight_layout()
            plt.show()
