import pandas as pd
from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats.mstats import mode
from sklearn.decomposition import PCA
from scipy.spatial.distance import cdist, pdist
from sklearn.datasets.samples_generator import make_regression
from sklearn import datasets, linear_model
from os import listdir
from os.path import isfile, join
import os
import sys
import glob
import errno

def create_dataframes(target_name, num): 	

	# target_names = ['AddAdhd','Alzheimers','Autism',
	# 'BirthControl','Cancer','Depression',
	# 'Diabetes','HeartDiseases','HivAids','Psychology','Schizophrenia','StemCells']
	# targets = [1,2,3,4,5,6,7,8,9,10,11,12]
	# target_reference = dict(zip(targets,target_names))
	# print target_reference

	mypath = "/Users/surabhiravishankar/Spring/EECS499_Larry/data/"+target_name
	onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
	# print onlyfiles
	abstract_list = []
	# data = {} makes a dictionary of key value pairs
	# you can read all the data
	data = {}
	for dir_entry in os.listdir(mypath):
	    dir_entry_path = os.path.join(mypath, dir_entry)
	    if os.path.isfile(dir_entry_path):
	        with open(dir_entry_path, 'r') as my_file:
	            data[dir_entry] = my_file.read()

	new_df = pd.DataFrame(data.items(), columns=['FileName', 'Abstract'])

	new_df['TargetNames']=target_name
	
	new_df['Targets']=num 

	return new_df

target_names = ['AddAdhd','Alzheimers','Autism',
	'BirthControl','Cancer','Depression',
	'Diabetes','HeartDiseases','HivAids','Psychology','Schizophrenia','StemCells']

add_adhd_df = create_dataframes(target_names[0],0)
alz_df = create_dataframes(target_names[1],1)
aut_df = create_dataframes(target_names[2],2)
birth_ctrl_df = create_dataframes(target_names[3],3)
cancer_df = create_dataframes(target_names[4],4)
depp_df = create_dataframes(target_names[5],5)
diabetes_df = create_dataframes(target_names[6],6)
heart_df = create_dataframes(target_names[7],7)
#hiv_aids_df = create_dataframes(target_names[8],8)
psychology_df = create_dataframes(target_names[9],9)
schizo_df = create_dataframes(target_names[10],10)
stem_df = create_dataframes(target_names[11],11)

# Attach all the frames 
frames = [add_adhd_df,alz_df,aut_df,cancer_df,depp_df,diabetes_df]
result = pd.concat(frames)

train, test = train_test_split(result, test_size = 0.2)

# Tokenizing 
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(train['Abstract'])
X_train_counts.shape


tf_transformer = TfidfTransformer(use_idf=False).fit(X_train_counts)
X_train_tf = tf_transformer.transform(X_train_counts)
X_train_tf.shape


tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
X_train_tfidf.shape

#docs_test = test['Abstract']

docs_test = ['Diabetes mellitus (DM), commonly referred to as diabetes, is a group of metabolic diseases in which there are high blood sugar levels over a prolonged period.[2] Symptoms of high blood sugar include frequent urination, increased thirst, and increased hunger. If left untreated, diabetes can cause many complications.',
	'Alzheimers disease (AD), also known as Alzheimer disease, or just Alzheimers, accounts for 60% to 70% of cases of dementia.[1][2] It is a chronic neurodegenerative disease that usually starts slowly and gets worse over time',
	'Attention deficit hyperactivity disorder (ADHD) and attention deficit disorder (ADD) symptoms may begin in childhood and continue into adulthood. ADHD and ADD symptoms, such as hyperactivity, implulsiveness and inattentiveness, can cause problems at home, school, work, or in relationships','Autism is a neurodevelopmental disorder characterized by impaired social interaction, verbal and non-verbal communication, and restricted and repetitive behavior',
	'Cancer is a group of diseases in which cells are aggressive (grow and divide without respect to normal limits), invasive (invade and destroy adjacent tissues), and/or metastatic (spread to other locations in the body).']
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
text_clf = Pipeline([('vect', CountVectorizer()),('tfidf', TfidfTransformer()),('clf', SGDClassifier(loss='hinge', penalty='l2',alpha=1e-3, n_iter=5, random_state=42)),])
_ = text_clf.fit(train['Abstract'], train['TargetNames'])
predicted = text_clf.predict(docs_test)

print predicted 


# for doc, category in zip(docs_test, predicted):
# 	print('%r => %s' % (doc, train['Targets']))

# np.mean(predicted == test['Targets'])         

# METRICS 
# from sklearn import metrics
# print metrics.classification_report(test['Targets'],predicted,target_names=test['TargetNames'])

# print metrics.confusion_matrix(test['Targets'],predicted)

# Training the Classifier 
# from sklearn.naive_bayes import MultinomialNB
# clf = MultinomialNB().fit(X_train_tfidf, train['Targets'])


# docs_new = ['Alzheimers is bad','Autism is a disorder']
# X_new_counts = count_vect.transform(docs_new)
# X_new_tfidf = tfidf_transformer.transform(X_new_counts)

# predicted = clf.predict(X_new_tfidf)

# for doc, category in zip(docs_new, predicted):
# 	print('%r => %s' % (doc, train['Targets']))

# files=glob.glob(mypath)   
# for file in files:     
#     f=open(file, 'r')  
#     abstract_list.append(f.readlines())
#     f.close()

# print len(abstract_list)

# csv_path = 'clean_data.csv'

# target_path = 'targetData.csv'
# target_var = pd.read_csv(target_path)
# csv_var = pd.read_csv(csv_path)

# # Printing the length of the data read 
# print('Length of the data: ', len(csv_var))
# print('Length of the target data: ', len(target_var))

# data = []
# # create an array of variables that consists for the first row of values 
# for row in csv_var: 
# 	data.append(row)

# target_data = [] # Consists of the row headings 
# for r in target_var:
# 	target_data.append(r)

# # Create a data frame for original data 
# csv_df = pd.DataFrame(csv_var,columns=data)