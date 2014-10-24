import os,sys
import subprocess
import smtplib
import string
import glob
import threading
import re

# directory to copy from
source_dir = sys.argv[1]
# directory to copy to
dest_dir = sys.argv[2]

os.chdir(source_dir)
source_files = glob.glob('*.root')
os.chdir(dest_dir)
dest_files = glob.glob('*.root')

copy_method = 'dccp'
#copy_method = 'srmcp'

source_file_dict = {}
dest_file_dict = {}

duplicate_files = []

files_copied = []

files_to_copy = []

# Check source directory for files, and only don't include duplicates. 
for file in source_files:
	# Use regexp to get the file name up to and including the job number
	job_id = re.findall(r".{1,99}_FlatNTuple_.[0-9]{0,5}_", file)[0]
	
	# Add to the dict, and if it appears more than once, it's a dupe
	if job_id not in source_file_dict:
		source_file_dict[job_id] = 1
	else:
		duplicate_files.append(file)

# Check the destination directory for files that are already there
for file in dest_files:
	# Use regexp to get the file name up to and including the job number
	job_id = re.findall(r".{1,99}_FlatNTuple_.[0-9]{0,5}_", file)[0]
	
	if job_id in source_file_dict:
		files_copied.append(file)


print 'There are a total of '+str(len(source_file_dict))+' unique files in the source directory and '+str(len(files_copied))+' files in the destination directory'

# Loop over all files in the source directory and copy them if they aren't duplicates, and aren't in the destination dir already
for file in source_files:
	if file not in duplicate_files and file not in files_copied:
		files_to_copy.append(file)

class RunCmd(threading.Thread):
    def __init__(self, cmd, timeout):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.timeout = timeout

    def run(self):
		with open(os.devnull, 'w') as fp:
			self.p = subprocess.Popen((self.cmd), stdout=fp)
			self.p.communicate()[0]
			self.p.wait()

    def Run(self):
        self.start()
        self.join(self.timeout)

        if self.is_alive():
            self.terminate()
            self.join()

file_iter = 0

for file in files_to_copy:
	file_iter += 1
	if copy_method == 'srmcp':
		source_str = "srm://maite.iihe.ac.be:8443/"+os.path.join(source_dir, file)
		dest_str = "file:///"+os.path.join(str(dest_dir), file)
	elif copy_method == 'dccp':
		source_str = os.path.join(source_dir, file)
		dest_str = os.path.join(dest_dir, file)


	# perfom the copy operation on each file
	print "From " + source_str + " to " + dest_str + " ("+str(file_iter)+"/"+str(len(source_file_dict))+")"

	# Run the copy job with a 60 second timeout in case of a stuck pnfs
	if copy_method == 'srmcp':
		RunCmd(["srmcp", source_str, dest_str], 120).run()
	elif copy_method == 'dccp':
		RunCmd(["dccp", source_str, dest_str], 120).run()
