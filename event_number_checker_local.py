import os,sys,glob
import array
import ROOT
#from ROOT import TFile #, TProfile, TNtuple


# Take directory name as executing argument, and change to the directory
dirname = sys.argv[1]
if len(sys.argv) > 2:
	match = sys.argv[2]
d = os.getcwd()
os.chdir(dirname)

ROOT.gSystem.Load('/user_mnt/user/mccartin/CMSSW/CMSSW_5_3_10_patch2/lib/slc5_amd64_gcc462/pluginanalysersFlatNTuples.so')

# Loop over the files in the directory containing the string 'Data_' in the filename
if len(sys.argv) > 2:
	fnames = sorted(glob.glob(dirname+match+'*.root'))
else:
	fnames = sorted(glob.glob(dirname+'*.root'))
LOG_EVERY_N = 2
k = 0

print 'Reading a total of '+str(len(fnames))+' files... \n'

events_set = set()
event_dict = {}
duplicates = []

for file in fnames:

	if (k % LOG_EVERY_N) == 0:
		outfile = open('duplicates_'+str(k)+'.txt','w+')
	
	outfile.write('processing: ' +str(file) + ' \n')

	print "processing " + str(file) + ' (' + str(k) + ' of ' + str(len(fnames))+')'

	file_to_check = ROOT.TFile( file )
	tree = file_to_check.Get('tree')

	nentries = tree.GetEntries()

	j = 0

 	for event in tree:
		j += 1
 		for branch in event.evt_info:
 			event_number = str(int(branch.event_number))
			run_number = str(int(branch.run))

			if run_number not in event_dict.keys():
				event_dict[run_number] = []
				event_dict[run_number].append(event_number)
			else:
				if event_number not in event_dict[run_number]:
					event_dict[run_number].append(event_number)
				else:
					print 'duplicate event found! evt: ' + run_number+'_'+event_number
					duplicates.append(run_number+'_'+event_number)

	if (k % LOG_EVERY_N) == 0:
		for id in duplicates:
			outfile.write(id+'\n')

			#id = run_no+event_no
			#print id

			#print id
  			#if id not in events_set:
			#events_set.add(event)
			# if id not in event_dict:
  			# 	event_dict[id] = 1
  			# else:
  			# 	print 'duplicate event found! evt: '+str(id)
 			# 	duplicates.append(event)

	k += 1

print len(duplicates)

# 	print 'Reading list of events'
# 	for event in events:
			
# print event_info
