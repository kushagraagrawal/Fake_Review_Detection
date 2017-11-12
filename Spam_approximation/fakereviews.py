'''
	Script for detecting fake reviews via a pre-trained classifier. Trains a Support Vector Machine  on the Yelp Review Dataset (op_spam_v1.4).
	Treats the classification of unseen examples as a regression problem and thus gives a value between -1 and 1 for the unseen examples.
'''

'''
	Dependencies for the script. Libraries used:
	1) Pandas
	2) OS
	3) NLTK
	4) Scikit-Learn
	5) Warnings
	6) FeatureClass (featureclass)
	7) JSON
	8) NUMPY
'''

import pandas as pd
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import pos_tag 
from gensim import matutils, corpora, models
from sklearn import cross_validation
from sklearn.grid_search import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.svm import NuSVC

import warnings
from featureclass import FeatureClass
from sklearn import svm
import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn import preprocessing
from sklearn.decomposition import PCA
'''
	Preprocessing the training data.
	Takes the list of files as input along with the root directory of the file and polarity and converts to a pandas dataframe.
'''

negative_list = os.listdir("negative_polarity")
positive_list = os.listdir("positive_polarity")

def preprocess(files_list,root_dir,polarity):
	labeled_class = []
	reviews = []
	actual_class = []
	for j in files_list:
		labeled_class.append(polarity)
		k = str(open(root_dir + '/' + j).read())
		reviews.append(k)
		actual_class.append(str(j.split('_')[0]))
	data = pd.DataFrame({'labeled_class':labeled_class,'review':reviews,'actual_class':actual_class})
	return data

negative_df = preprocess(negative_list, 'negative_polarity','negative')
positive_df = preprocess(positive_list, 'positive_polarity','positive')

'''
	Labeling the training data. Labelled 1 if they are true reviews and -1 if they are spam.
	For example, if the labeled class was positive and actual class is d(i.e. deceptive) it is a fake review.
'''
target = []
for i in positive_df.index:
	if ((positive_df['labeled_class'][i] == 'positive') & (positive_df['actual_class'][i] == 't')):
		target.append(1)
	elif ((positive_df['labeled_class'][i] == 'positive') & (positive_df['actual_class'][i] == 'd')):
		target.append(-1)
	else:
		print 'Error'
positive_df['target'] = target

target = []
for i in negative_df.index:
	if ((negative_df['labeled_class'][i] == 'negative') & (negative_df['actual_class'][i] == 't')):
		target.append(1)
	elif ((negative_df['labeled_class'][i] == 'negative') & (negative_df['actual_class'][i] == 'd')):
		target.append(-1)
	else:
		print "Error"
negative_df['target'] = target

data = positive_df.merge(negative_df,how='outer')
data = data[['review','target']]

'''
	Using scikit-learn's SVR function for support vector machine regression. Takes a list of list for training data and another vector for labels.
	X here is the list of feature vectors corresponding to each review. Feature vectors are made using FeatureClass defined in featureclass.py
	y is the label vector. Formed during preprocessing.
'''
y = data['target']
X = []
index = 0
feature_for_review = FeatureClass()

for items in data['review']:
	features = feature_for_review.add_features(items)
	
	X.append(features.values())
	for key in features.keys():
		data.loc[index,key] = features[key]
	index += 1
#print data.head()
'''
	feature scaling
'''

X = preprocessing.scale(X)
'''
	Training the regression model.
'''


     

clf = svm.SVR()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.33, random_state=42)
pca = PCA(n_components = 9)
pca.fit(X_train)
X_t_train = pca.transform(X_train)
X_t_test = pca.transform(X_test)
clf.fit(X_train,y_train)
print clf.score(X_t_test,y_test)

'''
	Testing the model on unlabeled reviews. All the unlabled reviews are in the JSON file hotelreviewsupdated.json.
	Each of the reviews are then converted to a feature vector and the SVR model is fit to find the extent of spam in the review.
	Gives a value between -1 and 1
	Note- There have been a few outliers where values are > 1 . Either remove them or just consider them as not spam.
'''


jsonfile = open('hotelreviewsupdated.json','r')
json_text = json.load(jsonfile)
final = []
index = 1
for items in json_text:
	if index <= 1000:
		feature = feature_for_review.add_features(items['content'])
		test = feature.values()
		test = np.array(test)
		test = test.reshape(1,-1)
		#test = pca.transform(test)
		temp = clf.predict(test)
		final.append(temp[0])
		index += 1
	else:
		break
	
print final

