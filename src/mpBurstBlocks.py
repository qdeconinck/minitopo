import numpy as np
import os as os
import matplotlib.pyplot as plt

class BurstBlocksAggregator:
	def __init__(self, yml, test_name, dest_dir):
		# csv_file="c2s_seq_1.csv"
		# minimum delay to observe to identify the beginning of a block
		self.min_block_sep = 0.3 
		self.headers = [ "ts", "map_begin", "subflow", "is_seq", "map_end", "is_reinject" ] 
		self.log = open(dest_dir+"/burst_block_aggregator.log","w")
		self.csv_file=dest_dir+"/"+"c2s_seq_1.csv"
		self.a = np.genfromtxt (self.csv_file, delimiter=",")
		self.blocks=[]
		self.times=[]
		self.packets_per_flow=[]
		self.flows_ratios = []
		self.subflows=[]
		self.flows_ratios=[]
		self.extract_blocks()
		self.extract_times()
		self.extract_flows_packets()
		self.extract_flows_ratios()

	def c(self,column):
		"""Return column index corresponding to name passed as argument"""
		return self.headers.index(column)
	def extract_blocks(self):
		# beginning of block. First block starts at packet 0
		b=0
		# iteration, we can start at packet 1
		i=1
		previous=0
		while i<len(self.a):
			if self.a[i][self.c("is_seq")]==1:
				# in this case we look for the start of a new sending block
				if b==None:
					b=i
					print >>self.log, "previous seq packet:", "{:10.8f}".format(self.a[previous][self.c("ts")]), "seq:", self.a[previous][self.c("map_begin")]
					print >>self.log, "found block starting at ", "{:10.8f}".format(self.a[i][self.c("ts")]), "seq:", self.a[i][self.c("map_begin")]
				# we know the start of the block and look for its last packet
				elif self.a[i][self.c("ts")]-self.a[previous][self.c("ts")]>self.min_block_sep:
					print >>self.log, "next block:", "{:10.8f}".format(self.a[i+1][self.c("ts")]), "seq:", self.a[i+1][self.c("map_begin")]
					print >>self.log,"--------------------------------------"
					# the ranges we use here are inclusive, ie the range contains both elements.
					self.blocks.append((b,previous))
					b=i
				# keep track of previous seq packet
				previous=i
			i=i+1
		self.blocks.append((b,previous))
		print >>self.log, "# blocks: ", len(self.blocks)
	def extract_times(self):
		for i in range(len(self.blocks)):
			print >>self.log, "Block " + str(i)
			print >>self.log, "---------------------"
			first,last = self.blocks[i]
			print >>self.log, "first packet[" + str(first) +"] at:", "{:10.6f}".format(self.a[first][self.c("ts")]), "seq:", self.a[first][self.c("map_begin")]
			print >>self.log, "last packet [" + str(last) +"] at :", "{:10.6f}".format(self.a[last][self.c("ts")]), "seq:", self.a[last][self.c("map_begin")]
			t1 = self.a[first][self.c("ts")]
			# +1 because our ranges are inclusive
			packets = self.a[first:last+1]
			biggest_seq_index=self.find_biggest_seq_in_block(packets)
			biggest_seq = packets[biggest_seq_index][self.c("map_end")]
			print >>self.log, "biggest_seq = " + str(biggest_seq)
			ack_index, ack_packet=self.find_ack_for_seq(biggest_seq, biggest_seq_index)
			print >>self.log, "ack time = " + "{:10.6f}".format(self.a[ack_index][self.c("ts")])
			print >>self.log, "ack index = " + str(ack_index)
			print >>self.log, "block time = " + "{:10.6f}".format(ack_packet[self.c("ts")] - packets[0][self.c("ts")])
			self.times.append([first, ack_index, ack_packet[self.c("ts")] - packets[0][self.c("ts")]   , packets[0][self.c("ts")], ack_packet[self.c("ts")]  ]) 
			print >>self.log, "############################"
		print >>self.log, "---------------------------------------------"
		print >>self.log, "block times = " + str(self.times)
		self.times = np.array(self.times)
		np.set_printoptions(precision=6)
		block_times= self.times[:,2]
		self.block_times=block_times
		# this was to drop the smallest and biggest values from the mean
		# block_times.sort()
		# self.block_times=block_times[1:-2]
	def extract_flows_packets(self):
		for i in range(len(self.blocks)):
			# will hold number of packets per flow for this block
			r={}
			print >>self.log, "Block " + str(i)
			print >>self.log, "---------------------"
			first,last = self.blocks[i]
			# +1 because our ranges are inclusive
			packets = self.a[first:last+1]
			for p in packets:
				if p[self.c("is_seq")]==0:
					continue
				flow = int(p[self.c("subflow")])
				if flow in r.keys():
					r[flow]+=1
				else:
					r[flow]=1
			self.packets_per_flow.append(r) 
			print >>self.log, r
			print >>self.log, "############################"
		print >>self.log, "---------------------------------------------"
		# now set values to 0 as needed for block that didn't send on some subflows
		sublist = [ h.keys() for h in self.packets_per_flow]
		all_subflows = list( set ( [item for sublist in self.packets_per_flow for item in sublist] ))
		self.subflows= all_subflows
		for h in self.packets_per_flow:
			for f in all_subflows:
				if not f in h.keys():
					h[f]=0

	def extract_flows_ratios(self):
		# reset value
		self.flows_ratios = []
		# for each block compute the ratio
		for count in self.packets_per_flow:
			total_packets = sum(count.values())
			h = {}
			for s in self.subflows:
				h[s]=count[s]/float(total_packets)
			self.flows_ratios.append(h)


	def find_ack_for_seq(self, seq, start_index):
		i=start_index
		while i<len(self.a):
			# find ack packets
			if self.a[i][self.c("is_seq")]==0:
				if self.a[i][self.c("map_begin")]>=seq:
					return (i,self.a[i])
			i=i+1
		return None

	def find_biggest_seq_in_block(self, packets):
		biggest_seq=-1
		j=0
		while j<len(packets):
			if packets[j][self.c("is_seq")]==1:
				if biggest_seq==-1:
					biggest_seq=j
				elif packets[j][self.c("map_begin")]>packets[biggest_seq][self.c("map_begin")]:
					biggest_seq=j
			j=j+1
		return biggest_seq
		
	def __del__(self):
		self.log.close()

	def __str__(self):
		s =   str(self.block_times) + "\nmean:\t" + str(self.block_times.mean()) +"\nstd:\t"+ str(self.block_times.std())
		s+= "\nPackets per flow:\n"
		s += str(self.packets_per_flow)
		s+= "\nRatio of packets per flow:\n"
		s += str(self.flows_ratios)
		return s
	def plot(self):
		ratio1 = plt.plot([ h[1] for h in self.flows_ratios ] , label = "flow 1 ratio")
		ratio2 = plt.plot([ h[2] for h in self.flows_ratios ] , label = "flow 2 ratio")
		times  = plt.plot(self.block_times, label = 'block time' )
		plt.legend(["ratio1", "ratio2", "times"])
		plt.show()
