

from mpTcptraceData import *
from subprocess import check_output

import numpy as np


# to get a REPL:
#import code
#code.interact(local=locals()) 



# A checker runs tests, and a test is made of multiple validations


# For a validation, the value to compare to is the target value from the yaml
# The validation takes place in the validate method, which takes
# as argument a value from which to extract the value to compare or the value itself
class Validation:
	def __init__(self, yml):
		if "target" in yml:
			self.compared=yml["target"]
		else:
			self.compared=None
	def name(self):
		return self.__class__.__name__
	def validate(self,value):
		raise Exception("Method not implemented")
	def setup(self):
		raise Exception("Method not implemented")


# checks a value passed is greater or equal (generic)
class MinValueValidation(Validation):
	def validate(self, value):
		self.value = value
		return self.compared<=value
# checks a value passed is greater or equal (generic)
class MaxValueValidation(Validation):
	def validate(self, value):
		self.value = value
		return self.compared>=value
# checks a value passed is greater or equal (generic)
class ExactValueValidation(Validation):
	def validate(self, value):
		self.value = value
		return self.compared==value


# the method get_tested_value of the tester returns the value passed to validate.
# the CsvTester returns an array of values
class MinDifferenceValidation(Validation):
	def validate(self, value):
		v = value.flatten()
		if len(v)>2:
			raise Exception("MinDifferenceValidation requires 2 values maximum, not "+ str(len(v)))
		self.value = float(v[1])-float(v[0])
		return self.compared<=self.value
class MinRowsValidation(Validation):
	def validate(self, value):
		self.value =  len(value)
		return self.compared<=self.value
class MaxRowsValidation(Validation):
	def validate(self, value):
		self.value =  len(value)
		return self.compared>=self.value
class ExactRowsValidation(Validation):
	def validate(self, value):
		self.value =  len(value)
		return self.compared==self.value
class MaxRatioValidation(Validation):
	def validate(self, value):
		v = value.flatten()
		if len(v)>2:
			raise Exception("MinDifferenceValidation requires 2 values maximum, not "+ str(len(v)))
		self.value = float(v[1])/(float(v[0])+float(v[1]))
		return self.compared>=self.value
# validates all values passed have increasing values
# it is the Tester's get_tested_value method that does the work
# to extract the values list from the trace.
class IncreasingValuesValidation(Validation):
	def validate(self, values):
		previous = 0
		for i,v in enumerate(values.flatten()):
			#print i, "{:10.6f}".format(previous), "{:10.6f}".format(v)
			if v<previous:
				self.value= "row " + str(i) # index of error row 
				return False
			else:
				previous=v
		return True



class Tester:
	def __init__(self, yml, trace):
		self.yml = yml
		self.trace = trace
	# performs a validation found in the yml file.
	def validate(self):
		is_ok = True
		self.logs = ""
		for val in self.yml["validations"]:
			tested_value = self.get_tested_value(val) 
			klass_name=val["name"].title().replace("_","")+"Validation"
			tester_klass=globals()[klass_name]
			tester = tester_klass(val)
			if "target" in val:
				target=val["target"]
			else:
				target=None

			try:
				if tester.validate(tested_value):
					self.logs=self.logs+ " " + "  OK  :" + val["desc"] +" - " + tester.name()+ " value : " + str(tester.value) + ("" if target==None else " vs target " + str(val["target"])) + "\n"
				else:
					self.logs=self.logs+ " " + "  FAIL:" + val["desc"] +" - " + tester.name()+ " value : " + str(tester.value) + ("" if target==None else " vs target " + str(val["target"])) + "\n"
					is_ok = False
			except Exception as e:
				self.logs=self.logs+ ("" if self.logs=="" else "\n ")+ "  EXCP:" + val["desc"] +" - " + tester.name()+ " " + str(e) + "\n"
		return is_ok
	def name(self):
		return self.__class__.__name__ 
	def get_tested_value(self,yml):
		raise Exception("Method not implemented")


# applies provided filter to Checker's trace, and returns number of lines in output(ie number of packets) 
class FilterTest(Tester):
	def get_tested_value(self, yml):
		if "filter" in self.yml:
			ret = check_output(["tshark", "-r", self.trace, "-Y", self.yml["filter"]])
			# -1 : substract line of sudo error message printed by tshark
			return len(ret.split("\n")) - 1
		else:
			raise Exception("Test requires a filter.")



class CsvTest(Tester):
	def get_tested_value(self, validation):
		a =  self.trace.get_csv(self.yml["csv"])
		if "rows" in self.yml:
			a = a[self.yml["rows"]]
		if "columns" in self.yml:
			a = a[:,self.yml["columns"]]
		return a


class Checker:
	def check(self):
		is_ok = True
		self.logs=self.test_id+"\n"
		if self.yml!=None:
			for test in self.yml:
				name=test["test"].title().replace("_","")+"Test"
				klass = globals()[name]
				r = klass(test, self.trace)
				if r.validate():
					self.logs = self.logs + " *" + self.test_id + " " + r.name() + " SUCCESS\n"
					self.logs = self.logs +  r.logs
				else:
					self.logs = self.logs + " *" + self.test_id + " " + r.name() + " FAIL\n"
					self.logs = self.logs + r.logs

# Runs tests based on tcptrace
# It (in the method inherited from its parent class) instanciates the ...Test class passing it the TcptraceData instance
class TcptraceChecker(Checker):
	def __init__(self, yml, test_id, destDir):
		self.yml = yml["tcptrace"]
		self.trace = TcptraceData(destDir+"/client.pcap")
		self.test_id = test_id

# Runs tests based on the tcpdump trace itself
class TsharkChecker(Checker):
	def __init__(self, yml, test_id, destDir):
		self.yml = yml["tshark"]
		self.trace = destDir+"/client.pcap"
		self.test_id = test_id

from mpMptcptraceData import *

# Runs tests based on mptcptrace
# It (in the method inherited from its parent class) instanciates the ...Test class passing it the MptcptraceData instance
class MptcptraceChecker(Checker):
	def __init__(self, yml, test_id, destDir):
		self.yml = yml["mptcptrace"]
		self.trace = MptcptraceData(destDir+"/client.pcap")
		self.test_id = test_id


