#!/usr/bin/python

import sys, getopt
from mpParamTopo import MpParamTopo
from mpMultiInterfaceTopo import MpMultiInterfaceTopo
from mpMultiInterfaceConfig import MpMultiInterfaceConfig
from mpMininetBuilder import MpMininetBuilder

topoParamFile = None
topoType      = "mininet"

def printHelp():
	print("Help Menu")

def parseArgs(argv):
	global topoParamFile
	try:
		opts, args = getopt.getopt(argv, "hf:", ["topoParam="])
	except getopt.GetoptError:
		printHelp()
		sys.exit(1)
	for opt, arg in opts:
		if opt == "-h":
			printHelp()
			sys.exit(1)
		elif opt in ("-f","--topoParam"):
			print("hllo", arg);
			topoParamFile = arg



if __name__ == '__main__':
	parseArgs(sys.argv[1:])
	if topoParamFile is None:
		print("Use command line param")
	else:
		param = MpParamTopo(topoParamFile)

	if topoType == "mininet":
		if param.getParam('topoType') == "MultiIf":
			mpTopo = MpMultiInterfaceTopo(MpMininetBuilder(), param)
			mpConfig = MpMultiInterfaceConfig(mpTopo, param)
			mpTopo.startNetwork()
			mpConfig.configureNetwork()
			mpConfig.pingAllFromClient()
			mpTopo.getCLI()
			mpTopo.stopNetwork()
	else:
		print("Unrecognized topo type")
	print(mpTopo)
