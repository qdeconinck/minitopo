#!/usr/bin/python

# apt-get install python-configglue

import sys, getopt
from mpXpRunner import MpXpRunner
from mpTopo import MpTopo

from shutil import copy
import os
from subprocess import call

import datetime
# currently all checkers and validations and defined in this file
from mpValidations import *

from yaml import load, dump

from optparse import OptionParser


# Define supported options
parser = OptionParser()
parser.add_option("-t", "--tests", dest="tests_dir",
                  help="Directory holding tests", metavar="TESTSDIR" , default="./tests")
parser.add_option("-l", "--logs", dest="logs_dir",
                  help="Directory where to log", metavar="LOGSDIR" , default="./logs")

(options, args) = parser.parse_args()

# initialise flags values
tests_dir=options.tests_dir.rstrip("/")
logs_dir=options.logs_dir.rstrip("/")

# take timestamp, used as subdirectory in logs_dir
timestamp=datetime.datetime.now().isoformat()

#timestamp = "2015-05-26T15:42:45.419949"

for test_name in [name for name in os.listdir(tests_dir) if os.path.isdir(os.path.join(tests_dir, name))]:
	# initialise files defining the experience and test
	test_dir =  tests_dir + "/" + test_name
	xpFile = test_dir+"/xp"
	topoFile = test_dir+"/topo"
	validation_file=test_dir+"/validation.yml"
	destDir=logs_dir+"/"+timestamp+"/"+test_name
	if not os.path.exists(destDir):
		os.makedirs(destDir)

	print "Running " + test_dir
	# run the experience
	MpXpRunner(MpTopo.mininetBuilder, topoFile, xpFile)

	#copy xp, topo and validation to log
	copy(topoFile,destDir) 
	copy(xpFile,destDir) 
	copy(validation_file,destDir) 
	#copy log files
        for l in ["client.pcap" ,"command.log" ,"upmc.log" ,"upms.log" ,"client.pcap" ,"netcat_server_0.log" ,"netcat_client_0.log"]:
		copy(l,destDir) 

	# Run validations
	with open(validation_file, 'r') as f:
		validations = load(f)
	for k in validations.keys():
		# Identify checker class
		name = k.title().replace("_","")+"Checker"
		klass= globals()[name]
		# instantiate checker with validations and test_name
		checker = klass(validations, test_name, destDir)
		if checker.check():
			print checker.logs
		else:
			print checker.logs






#tcptrace_checker = TcptraceChecker(validations, t )
#print "WILL VALIDATE"
#tcptrace_checker.check()

#for v  in validations["tcptrace"]:
#	print dump(v)

# /usr/local/bin/mptcptrace -f /tmp/dest/client.pcap -G20 -F3 -r7 -s -S -a



# Here are functions that can be used to generate topo and xp files:
#def write_entry(f, key, val):
#	f.write("{}:{}\n".format(key,val))
#	
#def generateTopo():
#	path="/tmp/topo"
#	f=open(path,"w")
#	# delay, queueSize (in packets), bw
#	write_entry(f, "path_0", "10,15,5")
#	write_entry(f, "path_1", "10,15,5")
#	write_entry(f, "topoType", "MultiIf")
#	f.close()
#	return path
#	
#def generateXp():
#	path="/tmp/xp"
#	f=open(path,"w")
#	write_entry(f, "xpType", "nc")
#	write_entry(f, "kpm", "fullmesh")
#	write_entry(f, "kpms", "netlink")
#	write_entry(f, "kpmc", "netlink")
#	write_entry(f, "upmc", "fullmesh")
##	write_entry(f, "upmc_args", "-t 600000 -i 500 -c 7800")
#	write_entry(f, "ddCount", "10000")
#	write_entry(f, "clientPcap", "yes")
#	write_entry(f, "ncClientPort_0", "0:33400")
#	write_entry(f, "rmem","300000 300000 300000")
#	f.close()
#	return path

#topoFile=generateTopo()
#print(topoFile)
#xpFile=generateXp()
#print(xpFile)

