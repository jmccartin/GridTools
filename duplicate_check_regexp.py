#! /usr/bin/python

import os
import sys
import re
import glob

# Initalise dictionaries
file_dict = {}
duplicate_files = []
dirnames = []

# Specify which directories you want to check (will do a duplicate scan across a maximum of two)
dirnames.append(sys.argv[1])
if len(sys.argv) > 2:
	dirnames.append(sys.argv[2])


# Loop over the files in the directory containing the string 'Data_' in the filename
for dirname in dirnames:
	fnames = glob.glob(dirname+'*.root')
	for file in fnames:
		# Use regexp to get the file name up to and including the job number
		job_id = re.findall(r".{1,99}_FlatNTuple_.[0-9]{0,5}_", file)[0]

		# Add to the dict, and if it appears more than once, it's a dupe
		if job_id not in file_dict:
			file_dict[job_id] = 1
		else:
			duplicate_files.append(file)

if len(duplicate_files) > 0:
	print 'Duplicates found:'
	for file in sorted(duplicate_files): 
		print file
	print ''
	print 'Checked a total of '+str(len(fnames))+' files and found '+str(len(duplicate_files))+' duplicates'
	prompt = raw_input('Delete duplicate files? [y/N] \n')
	if prompt == 'y':
		for file in sorted(duplicate_files):
			os.system('rm '+str(file))
else:
	print '\nNo duplicate files found in folder!'
	print 'Checked a total of '+str(len(fnames))+' files'
