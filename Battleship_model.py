
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier as RF
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import confusion_matrix

df_master = pd.read_csv("master.csv")
df_master.drop(labels="occupied_pct", axis=1, inplace=True)

df_sample = df_master
X = df_sample.drop(labels='occupied?', axis=1)
Y = df_sample["occupied?"]

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, train_size=0.7)

clf = RF(max_depth=15, n_estimators=20, n_jobs=-1, random_state=42)
clf.fit(X_train, Y_train)

import pickle

filename = "rf_classifier.sav"
pickle.dump(clf, open(filename, 'wb'))

# ----------------------------------------------------------------------------
# Grid Search

# search = GridSearchCV(clf,
#                       param_grid={"n_estimators":range(1,201,20), "max_depth":range(5,16,5)},
#                       scoring=["recall", "precision"],
#                       n_jobs=-1,
#                              verbose=1,
#                       refit="precision")
# search.fit(X_train, Y_train)
#
# df_search = pd.DataFrame(search.cv_results_)
#
# df_search.to_csv("search.csv", index=False)

# ----------------------------------------------------------------------------
# KNN

# from sklearn.neighbors import KNeighborsClassifier as KNN
#
# knn = KNN(n_neighbors=20)
# knn.fit(X_train, Y_train)
# print(knn.score(X_test, Y_test))
# Y_pred = knn.predict(X_test)
# print(confusion_matrix(Y_test, Y_pred))



