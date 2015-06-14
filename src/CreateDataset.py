#!/usr/bin/python
import os
import sys
import pandas as pd
import numpy as np

def create_topic(csv_file_name, dir_name,file_no):
	
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
		filename = str(file_no)+str(index)
		file1 = open(filename, "wb")
		file1.write(row['Abstract'])
		
def main(): 
	create_topic("AddAdhd.csv","AddAdhd",10)
	create_topic("Alzheimers.csv","Alzheimers",30)
	create_topic("Autism.csv","Autism",50)
	create_topic("BirthControl.csv","BirthControl",70)
	create_topic("Cancer.csv","Cancer",90)
	create_topic("HivAids.csv","HivAids",10)
	create_topic("Depression.csv","Depression",110)
	create_topic("Diabetes.csv","Diabetes",130)
	create_topic("HeartDiseases.csv","HeartDiseases",150)
	create_topic("Psychology.csv","Psychology",170)
	create_topic("Schizophrenia.csv","Schizophrenia",190)
	create_topic("StemCells.csv","StemCells",210)
	create_topic("Zoology.csv","Zoology",230)
	create_topic("Genetics.csv","Genetics",250)
	create_topic("Extinction.csv","Extinction",270)
	create_topic("Biotechnology.csv","Biotechnology",290)
	create_topic("VideoGames.csv","VideoGames",310)
	create_topic("ArtificialIntelligence.csv","ArtificialIntelligence",330)
	create_topic("Robotics.csv","Robotics",350)
	create_topic("VirtualReality.csv","VirtualReality",370)
	create_topic("ComputerSecurity.csv","ComputerSecurity",390)
	create_topic("Hurricanes.csv","Hurricanes",410)
	create_topic("Geology.csv","Geology",430)
	create_topic("Water.csv","Water",450)
	create_topic("Pollution.csv","Pollution",470)
	create_topic("GlobalWarming.csv","GlobalWarming",490)
	create_topic("EarthQuakes.csv","EarthQuakes",510)
	create_topic("Climate.csv","Climate",530)
	create_topic("Astrophysics.csv","Astrophysics",550)
	create_topic("DarkMatter.csv","DarkMatter",570)
	create_topic("Blackholes.csv","Blackholes",590)
	create_topic("Dinosaurs.csv","Dinosaurs",610)
	create_topic("Moon.csv","Moon",630)
	create_topic("Mars.csv","Mars",650)
	create_topic("SolarCells.csv","SolarCells",670)
	create_topic("WindEnergy.csv","WindEnergy",690)
	create_topic("SolarEnergy.csv","SolarEnergy",710)
	create_topic("NanoTechnology.csv","NanoTechnology",730)
	create_topic("FossilFuels.csv","FossilFuels",750)

if __name__ == "__main__":
    main()