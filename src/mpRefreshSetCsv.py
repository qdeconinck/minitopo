
import numpy as np
import os as os
import matplotlib.pyplot as plt
from subprocess import call,  check_call
from subprocess import check_output

class RefreshSetCsvAggregator:
	def __init__(self, yml, test_name, dest_dir):
		# csv_file="c2s_seq_1.csv"
		# minimum delay to observe to identify the beginning of a block

		self.paths_used=open("paths_used.log", "a")
		self.pcap_file=dest_dir+"/client.pcap"
                self.base_dir = os.path.dirname(self.pcap_file)
                working_dir =  os.getcwd()

                os.chdir(self.base_dir)
		check_call(["/usr/local/bin/mptcptrace" , "-f", os.path.basename(self.pcap_file) , "-G20",  "-F3",  "-r7",  "-s",  "-S", "-a", "-w2"])
		csv_content = check_output(["sudo", "tcptrace", "-l", "--csv", os.path.basename(self.pcap_file)])
		with (open("tcptrace.csv", "w")) as f:
			f.write(csv_content)
		time=os.system("cat stats_1.csv | grep Time | cut -d \";\" -f 4 >> /home/mininet/minitopo/src/times.log")
                os.chdir(working_dir)


		# for refresh_set:
		#self.headers = [ "decision", "port", "metric", "path" ] 
		#self.log = open(dest_dir+"/refresh_set_aggregator.log","w")
		#self.csv_file=dest_dir+"/"+"refresh_set.csv"
		#csv_content = check_output(["grep", "csv", dest_dir+"/upmc.log"])
		#with open(self.csv_file,"w") as f:
		#	f.write(csv_content)
		#self.a = np.genfromtxt (self.csv_file, delimiter=",")[:,1:]
		#self.a=np.array(self.a, dtype=int)
		#self.extract_data()
	def __del__(self):
		self.paths_used.close()
	def extract_data(self):
		decisions = np.unique(self.a[:,0])
		print decisions
		paths_used = []
		
		for decision in decisions:
			paths = np.array(filter(lambda row: row[0]==decision, self.a))
			print "paths for decision " + str(decision)
			print paths
			unique_paths = np.unique(paths[:, 3])
			print "unique paths:"
			print unique_paths
			print len(unique_paths)
			paths_used.append(len(unique_paths))
		print >>self.paths_used, paths_used
		print np.array(paths_used).argmax()


	def __str__(self):
		return "Nothing here, change it in mpRefreshSetCsv.py"
		#return self.csv_file
	def plot(self):
		pass
