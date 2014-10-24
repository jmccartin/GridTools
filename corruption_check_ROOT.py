import os,sys,glob

from ROOT import TFile #, TProfile, TNtuple
#from ROOT import gROOT, gBenchmark, gRandom, gSystem, Double, gStyle

# Take directory name as executing argument, and change to the directory
dirname = sys.argv[1]
d = os.getcwd()
os.chdir(dirname)

# Loop over the files in the directory containing the string 'Data_' in the filename
#fnames = os.listdir(dirname)
fnames = glob.glob(dirname+'*.root')
corruptedFiles = []

LOG_EVERY_N = 500
k = 0

print 'Reading a total of '+str(len(fnames))+' files... \n'

for file in fnames:
	k += 1
	matching = 0
	mapping = 0
	file_to_check = TFile( file )
	file_contents = file_to_check.GetListOfKeys()
	for i in file_contents:
		if "trigger_name_mapping" in str(i):
			matching = 1
		elif "tag_name_mapping" in str(i):
			mapping = 1
		check = mapping + matching
	if check != 2:
		corruptedFiles = "du -h " + str(os.path.join(dirname, file))
		print corruptedFiles
	file_to_check.Delete()

	if (k % LOG_EVERY_N) == 0:
		print "processing " + str(k) + ' of ' + str(len(fnames))
