# Stage 1. 
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import CountVectorizer 
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
import numpy as np 
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.grid_search import GridSearchCV

def contains(list, filter):
    for x in list:
        if filter(x):
            return True
    return False

# Function to Check if the article is a science article or not. 
def check_if_science(news_summary): 
	#Choose a small number of categories 
	categories = ['rec.autos',
	'rec.motorcycles',
	'rec.sport.baseball',
	'rec.sport.hockey',
	'talk.politics.misc',
	'talk.politics.guns',
	'talk.politics.mideast', 
	'talk.religion.misc',
	'alt.atheism',
	'soc.religion.christian',
	'misc.forsale',
	'sci.crypt',
	'sci.electronics',
	'sci.med',
	'sci.space']
	
	twenty_train = fetch_20newsgroups(subset='train', categories=categories, shuffle=True, random_state=42)

	#twenty_test = fetch_20newsgroups(subset='test',categories=categories,shuffle=True,random_state=42)

	docs_new = [] 
	docs_new.append(news_summary)

	#print("Pipelining and checking if SVM works better")
	text_clf = Pipeline([('vect', CountVectorizer()),('tfidf', TfidfTransformer()),('clf', SGDClassifier(loss='hinge', penalty='l2',alpha=1e-3, n_iter=5, random_state=42)),])
	_ = text_clf.fit(twenty_train.data, twenty_train.target)
	predicted = text_clf.predict(docs_new)
	
	# news_group consists of the categorized items that belong to the group.
	news_group = [] 

	for doc,category in zip(docs_new,predicted): 
		# print('%r => %s' % (doc, twenty_train.target_names[category]))
		# Create a list to make sure you can save which category it belongs to! 
		print "Stage 1: Article belongs to the Science Cateogy"
		news_group.append(twenty_train.target_names[category]) 

	# print (" SVM test ")		
	# print(np.mean(predicted == twenty_test.target))

	# ################################
	# # More detailed analysis       #
	# ################################

	# from sklearn import metrics
	# print("### Report: ")
	# print(metrics.classification_report(twenty_test.target, predicted, target_names=twenty_test.target_names))
	# print("### confusion matrix ")
	# print(metrics.confusion_matrix(twenty_test.target, predicted))
	

	# Grid Search 

	# parameters = {'vect__ngram_range': [(1, 1), (1, 2)],'tfidf__use_idf': (True, False),'clf__alpha': (1e-2, 1e-3),}

	# # Running the grid search classifier in parallel 
	# gs_clf = GridSearchCV(text_clf, parameters, n_jobs=-1)
	# gs_clf.fit(twenty_train.data, twenty_train.target)

	# # Predicting 
	# print("### Prediction after grid search")
	# print(twenty_train.target_names[gs_clf.predict([news_summary])])

	# ## Another option is to find the attribute with the best score 
	# best_parameters, score, _ = max(gs_clf.grid_scores_, key=lambda x: x[1])

	# print("### Printing best parameters")
	# for param_name in sorted(parameters.keys()):
	# 	 print("%s: %r" % (param_name, best_parameters[param_name]))

	# print("### Printing the score")
	# print(score)
	
	if contains(news_group, lambda x: x == 'rec.autos' or x == 'alt.atheism' or x == 'soc.religion.christian' or x == 'rec.motorcycles' or x == 'rec.sport.baseball' or x == 'rec.sport.hockey' or x == 'talk.religion.misc' or x == 'talk.politics.mideast' or x == 'talk.politics.guns' or x == 'talk.politics.misc' or x == 'misc.forsale'):
		return 0 
	else: 
		return 1