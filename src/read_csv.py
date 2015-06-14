#!/usr/bin/python
import os
import sys
import pandas as pd
import numpy as np

def create_topic(csv_file_name, dir_name):
	
	data_dir = "/Users/surabhiravishankar/Spring/EECS499_Larry/original_csv/"
	os.chdir(data_dir)
	corpus_path = csv_file_name
	corpus_var = pd.read_csv(corpus_path)

	print "Length of Corpus = ",len(corpus_var)
	field_names = [] 
	for row in corpus_var: 
		field_names.append(row)
	# Make a data frame 
	csv_df = pd.DataFrame(corpus_var,columns=field_names)

	abstract_df = csv_df['Abstract']

	path = "/Users/surabhiravishankar/Spring/EECS499_Larry/data/"+dir_name
	
	if not os.path.exists(path):
		os.mkdir(path,0755)
		os.chdir(path)
	else: 
		print "Path already exists!!"
		exit(0)

	# writing into the files 
	for index, row in csv_df.iterrows(): 
		print "writing file ... ", index
		filename = str(index)
		file1 = open(filename, "wb")
		file1.write(row['Abstract'])

create_topic("AddAdhd.csv","AddAdhd")
create_topic("Alzheimers.csv","Alzheimers")
create_topic("Autism.csv","Autism")
create_topic("BirthControl.csv","BirthControl")
create_topic("Cancer.csv","Cancer")
create_topic("Depression.csv","Depression")
create_topic("Diabetes.csv","Diabetes")
create_topic("HeartDiseases.csv","HeartDiseases")
create_topic("Psychology.csv","Psychology")
create_topic("Schizophrenia.csv","Schizophrenia")
create_topic("StemCells.csv","StemCells")
