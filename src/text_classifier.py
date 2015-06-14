###########################
# Categorizing text       #
###########################

# Choose a small number of categories 
categories = ['alt.atheism','sci.med']
from sklearn.datasets import fetch_20newsgroups
twenty_train = fetch_20newsgroups(subset='train', categories=categories, shuffle=True, random_state=42)

print ('###Twenty Train target names \n')
print (twenty_train.target_names)

print(len(twenty_train.data))
print(len(twenty_train.filenames))

# first line of the loaded data 
print("###First line of the loaded data \n")
print("\n".join(twenty_train.data[0].split("\n")[:3]))

print("###Target dataa")
print(twenty_train.target_names[twenty_train.target[0]])

# This contains the category integer id of each sample. 
# 1 corresponds to graphics 
# 3 corresponds to religion .. etc.. 
print("###Train Target 10 digits")
print(twenty_train.target[:10])

# Traget names is an attribute. which can be called 
print("###Getting the category names")
for t in twenty_train.target[:10]:
	print(twenty_train.target_names[t])
 
# Feature exraction starts here 
print("Feature exraction usin bag of words")

# Assign a fixed integer id to each workd occuring in any document of the training set 
# for each document i count the number of occurances of each word w and store it in X[i,j] as the value of 
# feature i where j is there index of teh word w in the dictionary 

# the bag of words representation implies that n_features is the number of distinct words in the corpus. this number is larger than 100,000

# scipy.sparse matrices are the data structures that do exactly this. there is built in support 

# tokenziing text 

# Count vectorizer supports counts of N-grams of words for consequective characters. 
# A dictionary of feature indicies are created. 

from sklearn.feature_extraction.text import CountVectorizer 
count_vect = CountVectorizer() 

X_train_counts = count_vect.fit_transform(twenty_train.data)

# Shape gives the size of the matrix 
print(X_train_counts.shape) 
print('###Vector Vocabulary') 
print(count_vect.vocabulary_.get(u'algorithm'))

#############################
# Occurance and frequencies #
#############################

from sklearn.feature_extraction.text import TfidfTransformer

# Fit methoid to fit the  to data and transform to transform the count-matrix to tf-idf representation 
# These two steps can be combined to achieve the same end result faster by skipping redundant processing. This is done through using the fit_transform(..)
tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)

X_train_tfidf = tf_transformer.transform(X_train_counts)

print("###Shape After tranforming and fitting")
print(X_train_tfidf.shape)

# Training the classifier using MultinomialNB 

from sklearn.naive_bayes import MultinomialNB
clf = MultinomialNB().fit(X_train_tfidf,twenty_train.target)

# Transform and fit the new test data 
docs_new = ['God is love','Open GL is GPU fast']
X_new_counts = count_vect.transform(docs_new)
X_new_tfidf = tf_transformer.transform(X_new_counts)

# Call the predict function to work the classifier 
predicted = clf.predict(X_new_tfidf)

for doc,category in zip(docs_new,predicted): 
	print('%r => %s' % (doc, twenty_train.target_names[category]))

#######################
# Building a Pipeline #
#######################

# In oder to make the) vectorizer to transformer to classifier to work, there is a pipleine class that behaves like a compound classifier

print("### Pipelining ")
from sklearn.pipeline import Pipeline
text_clf = Pipeline([('vect', CountVectorizer()),('tfidf', TfidfTransformer()),('clf', MultinomialNB()),])

text_clf = text_clf.fit(twenty_train.data,twenty_train.target)

###############################################
# Evalutation of performance on the test data #
###############################################

print("### Evaluation of Performance on the test set")
import numpy as np 
twenty_test = fetch_20newsgroups(subset='test',categories=categories,shuffle=True,random_state=42)
docs_test = twenty_test.data
predicted = text_clf.predict(docs_test)
print("### mean of TfidfTransformer")
print(np.mean(predicted == twenty_test.target))

################################
# Check if SVM performs better #
################################

print("Pipelining and checking if SVM works better")
from sklearn.linear_model import SGDClassifier
text_clf = Pipeline([('vect', CountVectorizer()),('tfidf', TfidfTransformer()),('clf', SGDClassifier(loss='hinge', penalty='l2',alpha=1e-3, n_iter=5, random_state=42)),])
_ = text_clf.fit(twenty_train.data, twenty_train.target)
predicted = text_clf.predict(docs_test)
print("### mean of SVM")
print(np.mean(predicted == twenty_test.target))

################################
# More detailed analysis       #
################################

from sklearn import metrics
print("### Report: ")
print(metrics.classification_report(twenty_test.target, predicted, target_names=twenty_test.target_names))
print("### confusion matrix ")
print(metrics.confusion_matrix(twenty_test.target, predicted))

################################
# Parameter issue       	   #
################################

# Instead of tweeking the parameters in different classifiers. There is something called 
# Grid Search. That uses a combination of parameters on a small test set, and it runs in
# parallel 

from sklearn.grid_search import GridSearchCV
parameters = {'vect__ngram_range': [(1, 1), (1, 2)],'tfidf__use_idf': (True, False),'clf__alpha': (1e-2, 1e-3),}

# Running the grid search classifier in parallel 
gs_clf = GridSearchCV(text_clf, parameters, n_jobs=-1)
gs_clf.fit(twenty_train.data, twenty_train.target)

# Predicting 
print("### Prediction after grid search")
print(twenty_train.target_names[gs_clf.predict(['God is love'])])

## Another option is to find the attribute with the best score 
best_parameters, score, _ = max(gs_clf.grid_scores_, key=lambda x: x[1])

print("### Printing best parameters")
for param_name in sorted(parameters.keys()):
	 print("%s: %r" % (param_name, best_parameters[param_name]))

print("### Printing the score")
print(score)

###### End ########