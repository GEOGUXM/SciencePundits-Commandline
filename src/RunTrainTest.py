import pandas as pd
import numpy as np
from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
import os
import sys
import glob
import CreateDataframe as cdf 
import ReadArticle as ra 
import CheckScience as cs
import PunditLookup as pl 
import TwitterStreaming as ts 
import time

def train_data(): 
	target_names = ['AddAdhd','Alzheimers','Autism',
	'BirthControl','Cancer','Depression',
	'Diabetes','HeartDiseases','HivAids','Psychology','Schizophrenia','StemCells',
	"Zoology","Genetics","Extinction","Biotechnology"
	,"VideoGames"
	,"ArtificialIntelligence"
	,"Robotics"
	,"VirtualReality"
	,"ComputerSecurity"
	,"Hurricanes"
	,"Geology"
	,"Water"
	,"Pollution"
	,"GlobalWarming"
	,"EarthQuakes"
	,"Climate"
	,"Astrophysics"
	,"DarkMatter"
	,"Blackholes"
	,"Dinosaurs"
	,"Moon"
	,"Mars"
	,"SolarCells"
	,"WindEnergy"
	,"SolarEnergy"
	,"NanoTechnology"
	,"FossilFuels"]

	# Create data frames for each category 
	add_adhd_df = cdf.create_dataframes(target_names[0],0)
	alz_df = cdf.create_dataframes(target_names[1],1)
	aut_df = cdf.create_dataframes(target_names[2],2)
	birth_ctrl_df = cdf.create_dataframes(target_names[3],3)
	cancer_df = cdf.create_dataframes(target_names[4],4)
	depp_df = cdf.create_dataframes(target_names[5],5)
	diabetes_df = cdf.create_dataframes(target_names[6],6)
	heart_df = cdf.create_dataframes(target_names[7],7)
	hiv_aids_df = cdf.create_dataframes(target_names[8],8)
	psychology_df = cdf.create_dataframes(target_names[9],9)
	schizo_df = cdf.create_dataframes(target_names[10],10)
	stem_df = cdf.create_dataframes(target_names[11],11)
	zoology_df = cdf.create_dataframes(target_names[12],12)
	genetics_df = cdf.create_dataframes(target_names[13],13)
	extinction_df = cdf.create_dataframes(target_names[14],14)
	biotech_df = cdf.create_dataframes(target_names[15],15)
	videogames_df = cdf.create_dataframes(target_names[16],16)
	ai_df = cdf.create_dataframes(target_names[17],17)
	robotics_df = cdf.create_dataframes(target_names[18],18)
	virtualreality_df = cdf.create_dataframes(target_names[19],19)
	computersecurity_df = cdf.create_dataframes(target_names[20],20)
	hurricanes_df = cdf.create_dataframes(target_names[21],21)
	geology_df = cdf.create_dataframes(target_names[22],22)
	water_df = cdf.create_dataframes(target_names[23],23)
	pollution_df = cdf.create_dataframes(target_names[24],24)
	globalwarming_df = cdf.create_dataframes(target_names[25],25)
	earthquakes_df = cdf.create_dataframes(target_names[26],26)
	climate_df = cdf.create_dataframes(target_names[27],27)
	astrophysics_df = cdf.create_dataframes(target_names[28],28)
	darkmatter_df = cdf.create_dataframes(target_names[29],29)
	blackholes_df = cdf.create_dataframes(target_names[30],30)
	dinosaurs_df = cdf.create_dataframes(target_names[31],31)
	moon_df = cdf.create_dataframes(target_names[32],32)
	mars_df = cdf.create_dataframes(target_names[33],33)
	solarcells_df = cdf.create_dataframes(target_names[34],34)
	windenergy_df = cdf.create_dataframes(target_names[35],35)
	solarenergy_df = cdf.create_dataframes(target_names[36],36)
	nanotechnology_df = cdf.create_dataframes(target_names[37],37)
	fossilfuels_df = cdf.create_dataframes(target_names[38],38)
	
	# Attach all the frames 
	frames = [add_adhd_df,
	alz_df, 	
	aut_df, 	
	birth_ctrl_df,	
	cancer_df, 	
	depp_df,  
	diabetes_df,  
	heart_df, 
	hiv_aids_df, 
	psychology_df,
	schizo_df,  
	stem_df,  
	zoology_df,  
	genetics_df,  
	extinction_df,
	biotech_df, 
	videogames_df, 
	ai_df,
	robotics_df, 
	virtualreality_df,
	computersecurity_df,
	hurricanes_df,
	geology_df,
	water_df,
	pollution_df, 
	globalwarming_df,
	earthquakes_df,
	climate_df,
	astrophysics_df,
	darkmatter_df,
	blackholes_df,
	dinosaurs_df, 
	moon_df,
	mars_df,
	solarcells_df,
	windenergy_df,
	solarenergy_df,
	nanotechnology_df,
	fossilfuels_df]
	
	result = pd.concat(frames)

	train, test = train_test_split(result, test_size = 0.2)

	text_clf = Pipeline([('vect', CountVectorizer()),('tfidf', TfidfTransformer()),('clf', SGDClassifier(loss='hinge', penalty='l2',alpha=1e-3, n_iter=5, random_state=42)),])
	_ = text_clf.fit(train['Abstract'], train['TargetNames'])

	return text_clf 
	
def test_data(text_clf,docs_test): 
	predicted = text_clf.predict(docs_test)
	return predicted 

def predict_category(): 
	# TODO 
	# take user input as url from here rather than the other thing. 
	# test_string = raw_input('Enter a newsarticle .. \n')
	article_url = raw_input('Please enter the url of the newsarticle \n')
	test_string = ra.extract_summary(article_url) 
	test_list = []
	test_list.append(test_string)
	keywords = ra.extract_keywords(article_url)

	# check if the article belongs to the science category or not. 

	res = cs.check_if_science(test_string)

	if res == 1: 
		# docs_test = ['Cancer grows out of normal cells in the body. Normal cells multiply when the body needs them, and die when the body doesnt need them. Cancer appears to occur when the growth of cells in the body is out of control and cells divide too quickly. It can also occur when cells forget how to die.','Diabetes mellitus (DM), commonly referred to as diabetes, is a group of metabolic diseases in which there are high blood sugar levels over a prolonged period.[2] Symptoms of high blood sugar include frequent urination, increased thirst, and increased hunger. If left untreated, diabetes can cause many complications.',
		# 'Alzheimers disease (AD), also known as Alzheimer disease, or just Alzheimers, accounts for 60% to 70% of cases of dementia.[1][2] It is a chronic neurodegenerative disease that usually starts slowly and gets worse over time',
		# 'Attention deficit hyperactivity disorder (ADHD) and attention deficit disorder (ADD) symptoms may begin in childhood and continue into adulthood. ADHD and ADD symptoms, such as hyperactivity, implulsiveness and inattentiveness, can cause problems at home, school, work, or in relationships','Autism is a neurodevelopmental disorder characterized by impaired social interaction, verbal and non-verbal communication, and restricted and repetitive behavior',
		# 'Cancer is a group of diseases in which cells are aggressive (grow and divide without respect to normal limits), invasive (invade and destroy adjacent tissues), and/or metastatic (spread to other locations in the body).']
		
		text_clf = train_data()
		predicted = test_data(text_clf,test_list)
		cat_dict = {'return_val': 1,
					'category' : predicted[0],
					'keywords': keywords}
		print "Stage 2: CATEGORY ------> ",cat_dict['category']
		return cat_dict
		# print 'The document was classified as: ', predicted[0]

	else: 
		cat_dict = {'return_val': 0,
					'category' : "Not a Science Article",
					'keywords' : [0]}
		return cat_dict

def get_expert_tweets(): 
	cat_dict = predict_category()
	if cat_dict['return_val'] == 1: 
		# do an expert look up 
		category = cat_dict['category']
		user_dict = pl.find_users(category)
		if user_dict['return_val'] == 1: 
			user_list = []
			user_list = user_dict['pundit_list']
			keywords = cat_dict['keywords']
			pundit_tweets = ts.get_timeline2(user_list,keywords)
			return pundit_tweets
	else: 
		# Return value will be zero 
		not_found = [{'score':0,'screen_name': "Null",'tweet':"Not a science article"}]
		return not_found

def main():
	while True: 
		print  "Enter Your Chouice: "
		print "\t 1. Enter News Article "
		print "\t 2. Exit"
		choice = raw_input()
		if choice == '1': 
			tweets2 = get_expert_tweets()
			for tweet in tweets2: 
				if(tweet['score'] > 1): 
					print tweet['screen_name'], ' tweeted ',tweet['tweet']
					time.sleep(2)
				elif(tweet['score']== 0): 
					print "The URL you entered is not a Science Article"
		else: 
			break


if __name__ == "__main__":
    main()

# def main(): 
# 	# TODO 
# 	# take user input as url from here rather than the other thing. 
# 	# test_string = raw_input('Enter a newsarticle .. \n')
# 	article_url = raw_input('Please enter the url of the newsarticle \n')
# 	test_string = ra.extract_summary(article_url) 
# 	test_list = []
# 	test_list.append(test_string)

# 	# check if the article belongs to the science category or not. 

# 	res = cs.check_if_science(test_string)

# 	if res == 1: 
# 		# docs_test = ['Cancer grows out of normal cells in the body. Normal cells multiply when the body needs them, and die when the body doesnt need them. Cancer appears to occur when the growth of cells in the body is out of control and cells divide too quickly. It can also occur when cells forget how to die.','Diabetes mellitus (DM), commonly referred to as diabetes, is a group of metabolic diseases in which there are high blood sugar levels over a prolonged period.[2] Symptoms of high blood sugar include frequent urination, increased thirst, and increased hunger. If left untreated, diabetes can cause many complications.',
# 		# 'Alzheimers disease (AD), also known as Alzheimer disease, or just Alzheimers, accounts for 60% to 70% of cases of dementia.[1][2] It is a chronic neurodegenerative disease that usually starts slowly and gets worse over time',
# 		# 'Attention deficit hyperactivity disorder (ADHD) and attention deficit disorder (ADD) symptoms may begin in childhood and continue into adulthood. ADHD and ADD symptoms, such as hyperactivity, implulsiveness and inattentiveness, can cause problems at home, school, work, or in relationships','Autism is a neurodevelopmental disorder characterized by impaired social interaction, verbal and non-verbal communication, and restricted and repetitive behavior',
# 		# 'Cancer is a group of diseases in which cells are aggressive (grow and divide without respect to normal limits), invasive (invade and destroy adjacent tissues), and/or metastatic (spread to other locations in the body).']
		
# 		text_clf = train_data()
# 		predicted = test_data(text_clf,test_list)
# 		print 'The document was classified as: ', predicted[0]

# 	else: 
# 		print 'The document does not belong to the science category. '

