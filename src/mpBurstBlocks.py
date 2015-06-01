import numpy as np
import os as os

class BurstBlocksAggregator:
	def __init__(self, yml, test_name, dest_dir):
		# csv_file="c2s_seq_1.csv"
		# minimum delay to observe to identify the beginning of a block
		self.min_block_sep = 0.1 
		self.headers = [ "ts", "map_begin", "subflow", "is_seq", "map-end", "is_reinject" ] 
		self.log = open(dest_dir+"/burst_block_aggregator.log","w")
		self.csv_file=dest_dir+"/"+"c2s_seq_1.csv"
		self.a = np.genfromtxt (self.csv_file, delimiter=",")
		self.blocks=[]
		self.times=[]
		self.extract_blocks()
		self.extract_times()

	def c(self,column):
		"""Return column index corresponding to name passed as argument"""
		return self.headers.index(column)
	def extract_blocks(self):
		# beginning of block. First block starts at packet 0
		b=0
		# iteration, we can start at packet 1
		i=1
		while i<len(self.a):
			if self.a[i][self.c("ts")]-self.a[i-1][self.c("ts")]>0.1:
				print >>self.log, "previous block:", "{:10.8f}".format(self.a[i-1][self.c("ts")]), "seq:", self.a[i-1][self.c("map_begin")]
				print >>self.log, "found block starting at ", "{:10.8f}".format(self.a[i][self.c("ts")]), "seq:", self.a[i][self.c("map_begin")]
				print >>self.log, "next block:", "{:10.8f}".format(self.a[i+1][self.c("ts")]), "seq:", self.a[i+1][self.c("map_begin")]
				print >>self.log,"--------------------------------------"
				# the ranges we use here are inclusive, ie the range contains both elements.
				self.blocks.append((b,i-1))
				b=i
			i=i+1
		self.blocks.append((b,i-1))
		print >>self.log, "# blocks: ", len(self.blocks)
	def extract_times(self):
		for i in range(len(self.blocks)):
			first,last = self.blocks[i]
			t1 = self.a[first][self.c("ts")]
			# +1 because our ranges are inclusive
			packets = self.a[first:last+1]
			j=0
			biggest_ack=-1
			while j<len(packets):
				if packets[j][self.c("is_seq")]==0:
					if biggest_ack==-1:
						biggest_ack=j
					elif packets[j][self.c("map_begin")]>packets[biggest_ack][self.c("map_begin")]:
						biggest_ack=j
				j=j+1
			self.times.append([first, first+biggest_ack, packets[biggest_ack][self.c("ts")] - packets[0][self.c("ts")], packets[0][self.c("ts")], packets[biggest_ack][self.c("ts")]]) 
		self.times = np.array(self.times)
		np.set_printoptions(precision=6)
		block_times= self.times[:,2]
		block_times.sort()
		self.block_times=block_times[1:-2]
	def __del__(self):
		self.log.close()

	def __str__(self):
		return  str(self.block_times) + "\nmean:\t" + str(self.block_times.mean()) +"\nstd:\t"+ str(self.block_times.std())
