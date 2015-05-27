#!/usr/bin/python


from subprocess import check_output
import csv

from io import StringIO
import re
import numpy as np




class TcptraceData:
	def __init__(self, pcap_file):
		self.pcap_file=pcap_file
		csv_content = check_output(["tcptrace", "-l", "--csv", pcap_file])
		tcptrace_reader = csv.reader(filter(lambda l: len(l)>0 and l[0]!="#",csv_content.splitlines()))
		cells=np.array(list(tcptrace_reader))
		#drop header row
		cells= cells[1:]
		self.cells = cells
		self.headers=cells[0]
		self.flows=cells[1:]
		self.number_of_flows=len(self.flows)
	def get_csv(self, name):
		return self.cells
