
import pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier as RF
from sklearn.model_selection import train_test_split, GridSearchCV

df_master = pd.read_csv("master.csv")
df_master.drop(labels="occupied_pct", axis=1, inplace=True)

df_sample = df_master
X = df_sample.drop(labels='occupied?', axis=1)
Y = df_sample["occupied?"]

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, train_size=0.7)

clf = RF(max_depth=15, n_estimators=20, n_jobs=-1, random_state=42)
clf.fit(X_train, Y_train)
filename = "rf_classifier.sav"
pickle.dump(clf, open(filename, 'wb'))

# Y_pred = clf.predict(X_test)
# print("Random Forest")
# print(confusion_matrix(Y_test, Y_pred))
# print("Precision: ", precision_score(Y_test, Y_pred))
# print("Recall: ", recall_score(Y_test, Y_pred))

# ----------------------------------------------------------------------------
# Grid Search

search = GridSearchCV(clf,
                      param_grid={"n_estimators":range(1,201,20), "max_depth":range(5,16,5)},
                      scoring=["recall", "precision"],
                      n_jobs=-1,
                      verbose=1,
                      refit="precision")
search.fit(X_train, Y_train)

df_search = pd.DataFrame(search.cv_results_)

df_search.to_csv("search.csv", index=False)

# ----------------------------------------------------------------------------
# KNN

# from sklearn.neighbors import KNeighborsClassifier as KNN
#
# knn = KNN(n_neighbors=20)
# knn.fit(X_train, Y_train)
# Y_pred = knn.predict(X_test)
#
# print("KNN")
# print(confusion_matrix(Y_test, Y_pred))
# print("Precision: ", precision_score(Y_test, Y_pred))
# print("Recall: ", recall_score(Y_test, Y_pred))
#
# ----------------------------------------------------------------------------
# Logistic Regression
#
# from sklearn.linear_model import LogisticRegression as LR
#
# lr = LR(random_state=42, n_jobs=-1)
# lr.fit(X_train, Y_train)
# Y_pred = lr.predict(X_test)
#
# print("Logistic Regression")
# print(confusion_matrix(Y_test, Y_pred))
# print("Precision: ", precision_score(Y_test, Y_pred))
# print("Recall: ", recall_score(Y_test, Y_pred))
#
# ----------------------------------------------------------------------------
# from sklearn.naive_bayes import GaussianNB as NB
# nb = NB()
# nb.fit(X_train, Y_train)
# Y_pred = nb.predict(X_test)
#
# print("Gaussian Naive Bayes")
# print(confusion_matrix(Y_test, Y_pred))
# print("Precision: ", precision_score(Y_test, Y_pred))
# print("Recall: ", recall_score(Y_test, Y_pred))

