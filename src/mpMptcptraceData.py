#!/usr/bin/python


from subprocess import check_call
import csv

from io import StringIO
import re
import os
import numpy as np




class MptcptraceData:
	def __init__(self, pcap_file):
		self.pcap_file=pcap_file
                self.base_dir = os.path.dirname(pcap_file)
                working_dir =  os.getcwd()

                # generate CSVs
                os.chdir(self.base_dir)
                print self.base_dir
                print os.getcwd()
		check_call(["sudo" , "/usr/local/bin/mptcptrace" , "-f", os.path.basename(pcap_file) , "-G20",  "-F3",  "-r7",  "-s",  "-S", "-a", "-w2"])
                os.chdir(working_dir)
        # accessing the attribute corresponding to the filename will parse the csv and return its cells
        def __getattr__(self, name):
                csv_file = self.base_dir+"/"+name+".csv"
                print "opening csv file " + csv_file
                if os.path.isfile(csv_file):
                        a = np.genfromtxt (csv_file, delimiter=",")
                        setattr(self, name, a)
                        return getattr(self,name)
                else:
                        raise AttributeError("No csv file for unknown attribute "+name)
                

	# gets cell corresponding to flow with header column 
	# flow 0 = first one, from 1=subflows
	def get(self, name):
                if hasattr(self,name):
                        return getattr(self,name)
                else:
                        return self.__get_attr__(name)
                

