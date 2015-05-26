#!/usr/bin/python


from subprocess import check_output
import csv

from io import StringIO
import re




class TcptraceData:
	def __init__(self, pcap_file):
		self.pcap_file=pcap_file
		csv_content = check_output(["tcptrace", "-l", "--csv", pcap_file])
		tcptrace_reader = csv.reader(filter(lambda l: len(l)>0 and l[0]!="#",csv_content.splitlines()))
		cells=list(tcptrace_reader)
		self.headers=cells[0]
		self.flows=cells[1:]
		self.number_of_flows=len(self.flows)
	# gets cell corresponding to flow with header column 
	# flow 0 = first one, from 1=subflows
	def get(self, flow, column):
		if flow>self.number_of_flows-1:
			raise Exception("Bad flow index")
		value = self.flows[flow][self.headers.index(column)]
		if re.search("[a-zA-Z]", value):
			return value
		elif re.search("\.", value):
			return float(value)
		elif re.search("^[0-9]+$", value):
			return int(value)
		else:
			return value

	# returns first packet time of flow
	def first_packet(self, flow):
		return float(self.flows[flow][self.header_index("first_packet")])-float(self.flows[0][self.header_index("first_packet")])
	# util: get column index based on header name
	def header_index(self, column):
		return self.headers.index(column)
	

	




#t = TcptraceData("client.pcap")
#print t.number_of_flows
#print t.first_packet(1)





