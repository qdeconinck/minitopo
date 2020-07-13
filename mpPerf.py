#!/usr/bin/python

import sys, getopt
from mpXpRunner import MpXpRunner
from mpTopo import MpTopo

topoParamFile = None
xpParamFile   = None
topoBuilder   = "mininet"

def printHelp():
	print("Help Menu")

def parseArgs(argv):
	global topoParamFile
	global xpParamFile
	try:
		opts, args = getopt.getopt(argv, "ht:x:", ["topoParam=","xp="])
	except getopt.GetoptError:
		printHelp()
		sys.exit(1)
	for opt, arg in opts:
		if opt == "-h":
			printHelp()
			sys.exit(1)
		elif opt in ("-x","--xp"):
			xpParamFile = arg
		elif opt in ("-t","--topoParam"):
			print("hey")
			topoParamFile = arg
	if topoParamFile is None:
		print("Missing the topo...")
		printHelp()
		sys.exit(1)

if __name__ == '__main__':
	parseArgs(sys.argv[1:])
	MpXpRunner(MpTopo.mininetBuilder, topoParamFile, xpParamFile)
