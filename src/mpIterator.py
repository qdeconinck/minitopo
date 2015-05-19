#!/usr/bin/python

import sys, getopt
from mpXpRunner import MpXpRunner
from mpTopo import MpTopo

from shutil import copy
import os
from subprocess import call

import datetime
from mpTcptraceData import *

from yaml import load, dump

topoParamFile = None
xpParamFile   = None
topoBuilder   = "mininet"

# A checker runs tests, and a test is made of multiple validations



# checks a value passed is greater or equel (generic)
class MinValueValidation:
	def __init__(self, yml):
		self.compared=yml["target"]
	def validate(self, value):
		return self.compared<=value

# individual flow validation (specific)
class MinDelayValidation:
	def __init__(self, v):
		self.compared=v["target"]
	def validate(self, flow):
		return self.compared<=flow[5]



# class testing tcptrace results
# the inheriting class should implement get_tested_value(self, yml)
class TcptraceTest: 
	def __init__(self, yml, trace):
		self.yml = yml["validations"]
		self.trace = trace
	# performs a validation found in the yml file.
	def validate(self):
		for val in self.yml:
			tested_value = self.get_tested_value(val) 
			klass_name=val["name"].title().replace("_","")+"Validation"
			tester_klass=globals()[klass_name]
			tester = tester_klass(val)
			if tester.validate(tested_value):
				print "SUCCESS"
			else:
				print "FAIL"
class NumberOfFlowsTest(TcptraceTest):
	def get_tested_value(self, yml):
		return self.trace.number_of_flows

class FlowsTest(TcptraceTest):
	def get_tested_value(self, yml):
		return self.trace.flows[yml["index"]]


class TcptraceChecker:
	def __init__(self, yml, trace):
		self.yml = yml["tcptrace"]
		self.trace = trace
	def check(self):
		for test in self.yml:
			name=test["test"].title().replace("_","")+"Test"
			klass = globals()[name]
			r = klass(test, self.trace)
			r.validate()



def write_entry(f, key, val):
	f.write("{}:{}\n".format(key,val))
	
def generateTopo():
	path="/tmp/topo"
	f=open(path,"w")
	# delay, queueSize (in packets), bw
	write_entry(f, "path_0", "10,15,5")
	write_entry(f, "path_1", "10,15,5")
	write_entry(f, "topoType", "MultiIf")
	f.close()
	return path
	
def generateXp():
	path="/tmp/xp"
	f=open(path,"w")
	write_entry(f, "xpType", "nc")
	write_entry(f, "kpm", "fullmesh")
	write_entry(f, "kpms", "netlink")
	write_entry(f, "kpmc", "netlink")
	write_entry(f, "upmc", "fullmesh")
#	write_entry(f, "upmc_args", "-t 600000 -i 500 -c 7800")
	write_entry(f, "ddCount", "10000")
	write_entry(f, "clientPcap", "yes")
	write_entry(f, "ncClientPort_0", "0:33400")
	write_entry(f, "rmem","300000 300000 300000")
	f.close()
	return path

timestamp=datetime.datetime.now().isoformat()
#topoFile=generateTopo()
#print(topoFile)
#xpFile=generateXp()
#print(xpFile)

topoFile="./conf/topo/simple_para"
xpFile="./conf/xp/4_nc"

#MpXpRunner(MpTopo.mininetBuilder, topoFile, xpFile)

destDir="/tmp/dest"
if not os.path.exists(destDir):
	os.makedirs(destDir)

#copy log files
copy("client.pcap",destDir) 
#copy xp and topo
copy(topoFile,destDir) 
copy(xpFile,destDir) 

#os.chdir(destDir)
#print(os.getcwd())
#call(["/usr/local/bin/mptcptrace", "-f", "/tmp/dest/client.pcap", "-G20", "-F3", "-r7", "-s", "-S", "-a"])

t = TcptraceData("/tmp/dest/client.pcap")
print "Number of flows:", t.number_of_flows
print "Time for fist flow:", t.first_packet(1)

validation_file="validation.yml"
with open(validation_file, 'r') as f:
	validations = load(f)
print validations

tcptrace_checker = TcptraceChecker(validations, t )
print "WILL VALIDATE"
tcptrace_checker.check()

#for v  in validations["tcptrace"]:
#	print dump(v)

# /usr/local/bin/mptcptrace -f /tmp/dest/client.pcap -G20 -F3 -r7 -s -S -a
