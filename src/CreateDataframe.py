import pandas as pd
import numpy as np
import os
import sys
import glob
import errno
from os import listdir
from os.path import isfile, join

def create_dataframes(target_name, num): 	
	mypath = "/Users/surabhiravishankar/Spring/EECS499_Larry/data/"+target_name
	onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
	# Create a dictionary consisting of data 
	data = {}
	for dir_entry in os.listdir(mypath):
	    dir_entry_path = os.path.join(mypath, dir_entry)
	    if os.path.isfile(dir_entry_path):
	        with open(dir_entry_path, 'r') as my_file:
	            data[dir_entry] = my_file.read()
	new_df = pd.DataFrame(data.items(), columns=['FileName', 'Abstract'])
	new_df['TargetNames']=target_name
	new_df['Targets']=num 
	# Returns a data frame that consists of filenames and abstracts for columns
	return new_df
