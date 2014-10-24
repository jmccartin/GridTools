#!/usr/bin/env python

import sys,os
import glob
import ConfigParser
import pickle, tempfile

crab_dir = sys.argv[1]

filenames = glob.glob(crab_dir + 'res/CMSSW_*.stdout')
crab_config = crab_dir+'share/crab.cfg'
pickled_file = crab_dir+'job/CMSSW.py.pkl'

reading_mode = 1

events_accepted = []
events_total    = []
dataset_total    = 0
dataset_accepted = 0
dataset_events = 0
bad_jobs = 0
n_read = 0
files_without_stats = 0

# Use ConfigParser to get the name of the dataset
config = ConfigParser.RawConfigParser()
config.read(crab_config)
datasetname = config.get('CMSSW', 'datasetpath')
datasetevents = int(config.get('CMSSW','total_number_of_events'))

# Create a temporary file to dump the python config in
temp = tempfile.TemporaryFile()

with open(pickled_file, 'rb') as input_file:
	pickled_string = pickle.load(input_file)
temp.write(str(pickled_string.dumpPython()))
temp.seek(0)

badfiles = []

# Read the config tempfile and get the preselection values (if any)
line = temp.readline()
print '--------------------------------------'
while line != '':
	if 'process.cleanPatJets =' in line:
		for i in range(6):
			line = temp.readline()
		if 'preselection' in line:
			print ' Jets:'
			print line
	if 'src = cms.InputTag(\"cleanPatJets\")' in line:
		line = temp.readline()
		print ' nJets:'
		print line
	if 'process.cleanPatElectrons =' in line:
		for i in range(6):
			line = temp.readline()
		if 'preselection' in line:
			print ' Electrons:'
			print line
	if 'process.cleanPatMuons =' in line:
		for i in range(6):
			line = temp.readline()
		if 'preselection' in line:
			print ' Muons:'
			print line

	line = temp.readline()


print 'processing a total of '+str(len(filenames))+' files'

# Loop over each CMSSW.out file and look for clean exit statuses.
for file in filenames:
	f = open(file)
	file_is_good = False
	for line in f:
		if 'JOB_EXIT_STATUS' in line:
			if 'JOB_EXIT_STATUS = 0' in line:
				n_read += 1
				continue
			else:
				bad_jobs += 1
				badfiles.append(file)
		
		if reading_mode == 1:
			if 'TrigReport Events' in line:
				content = [value for value in line.split()]
				events_accepted.append(content[7])
				events_total.append(content[4])
				dataset_total += int(content[4])
				dataset_accepted += int(content[7])
				file_is_good = True
		elif reading_mode == 2:
			if 'TrigReport' and 'HBHENoiseFilter' in line:
				content = [value for value in line.split()]
				if str(content[0]) == 'TrigReport':
					dataset_total += int(content[1])
			if 'TrigReport' and 'produceNTuples' in line:
				content = [value for value in line.split()]
				if str(content[0]) == 'TrigReport':
					if str(content[1]) != '1':
						dataset_accepted += int(content[1])
				file_is_good = True

	if not file_is_good:
		files_without_stats += 1

	f.close()



# 1600:TrigReport      20000      20000      19999          1          0 HBHENoiseFilter

print '------------------------------------------------------------'
print 'Dataset:            '+str(datasetname)
if datasetevents > 0:
	print 'Events in Dataset:  '+str(datasetevents)
print 'Events Passed:      '+str(dataset_accepted)
print 'Events Total:       '+str(dataset_total)
print 'Preselection Eff:   '+str(float(dataset_accepted)/float(dataset_total))
print 'There were a total of '+str(bad_jobs)+ ' jobs with non-zero exit codes'
print 'Efficiency calculated from a total of '+str(n_read)+' files'
print 'I could not parse statistics from '+str(files_without_stats)+' good jobs'
print '------------------------------------------------------------'
#Example ideal output (frequently gets cut by a 'BIG SNIP' however)
#TrigReport Events total = 1754 passed = 1752 failed = 2

#if len(badfiles) > 0:
#	print 'Files with non-zero exit codes:'
#	for file in badfiles:
#		print file
