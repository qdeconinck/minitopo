

from mpTcptraceData import *

import numpy as np


# A checker runs tests, and a test is made of multiple validations


# For a validation, the value to compare to is the target value from the yaml
# The validation takes place in the validate method, which takes
# as argument a value from which to extract the value to compare or the value itself
class Validation:
	def __init__(self, yml):
		self.compared=yml["target"]
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

# individual flow validation (specific)
# gets flow_spec = (index, flows) where index is the index of the flow to validate, and flows is the array of flows
class MinDelayValidation(Validation):
	def validate(self, flow_spec):
		(yml,trace) = flow_spec
		index=yml["index"]
		val = trace.first_packet(index)-trace.first_packet(0)
		self.value = val
		return self.compared<=val

# individual flow validation (specific)
# gets flow_spec = ( [ index0, index1] , flows) where:
#                      - index0 is the index of the flow taken as reference for timing
#                      - index1 is the flow for which we want to validate the timing
#                      - flows is the array of flows
class MinDelayBetweenValidation(Validation):
	def validate(self, flow_spec):
		(yml ,trace) = flow_spec
		[index0, index1] = yml["index"]
		val = trace.first_packet(index1)-trace.first_packet(index0)
		self.value = val
		return self.compared<=val

class AttributeValidation(Validation):
	def setup(self, flow_spec):
		(yml ,trace) = flow_spec
		[index0, index1] = yml["index"]
		self.val0 = trace.get(index0, yml["attribute"]) 
		self.val1 = trace.get(index1, yml["attribute"])

class AttributeMinimumDifferenceValidation(AttributeValidation):
	def validate(self, flow_spec):
		self.setup(flow_spec)
		self.value = self.val1 - self.val0
		return self.compared<=self.value

class AttributeMaximumDifferenceValidation(AttributeValidation):
	def validate(self, flow_spec):
		self.setup(flow_spec)
		self.value = self.val1 - self.val0
		return self.compared>=self.value


class AttributeMinimumRatioValidation(AttributeValidation):
	def validate(self, flow_spec):
		self.setup(flow_spec)
		self.value = float(self.val1)/+float(self.val1)
		return self.compared<=self.value

class AttributeMaximumRatioValidation(AttributeValidation):
	def validate(self, flow_spec):
		self.setup(flow_spec)
		self.value = float(self.val1)/float(self.val0)
		return self.compared>=self.value

class IncreasingValueValidation(AttributeValidation):
	def validate(self, values):
		previous = 0
		for i,v in enumerate(values):
			#print i, "{:10.6f}".format(previous), "{:10.6f}".format(v)
			if v<previous:
				self.value=i # index of error row 
				return False
			else:
				previous=v
		return self.compared>=self.value


class Tester:
	def __init__(self, yml, trace):
		self.yml = yml["validations"]
		self.trace = trace
	# performs a validation found in the yml file.
	def validate(self):
		is_ok = True
		self.logs = ""
		for val in self.yml:
			tested_value = self.get_tested_value(val) 
			klass_name=val["name"].title().replace("_","")+"Validation"
			tester_klass=globals()[klass_name]
			tester = tester_klass(val)
			try:
				if tester.validate(tested_value):
					self.logs=self.logs+ " " + "  OK  :" + val["desc"] +" - " + tester.name()+ " value : " + str(tester.value) +" vs " + str(val["target"]) + "\n"
				else:
					self.logs=self.logs+ " " + "  FAIL:" + val["desc"] +" - " + tester.name()+ " value : " + str(tester.value) +" vs " + str(val["target"]) + "\n"
					is_ok = False
			except Exception as e:
				self.logs=self.logs+ ("" if self.logs=="" else "\n ")+ "  EXCP:" + val["desc"] +" - " + tester.name()+ " " + str(e) + "\n"
		return is_ok
	def name(self):
		return self.__class__.__name__ 
	def get_tested_value(self,yml):
		raise Exception("Method not implemented")



# Base class testing tcptrace results
# the inheriting class should implement get_tested_value(self, yml)
# the get_tested_value should return the value that all validations of this test will use
# the validations get this value as argument of their validate method
# The validate method iterates one the validations mentioned for the test in the yml file.
class TcptraceTest(Tester):
	pass

# get_tested_value returns the number of flows
class NumberOfFlowsTest(TcptraceTest):
	def get_tested_value(self, yml):
		return self.trace.number_of_flows

# get_tested_value returns index of the flow to validate, and the list of flows
# index can be a compound value, as in the case of min_delay_between where it is an array of indexes
class FlowsTest(TcptraceTest):
	def get_tested_value(self, yml):
		return (yml,self.trace) 



		
class MptcptraceTest(Tester):
	pass

import code
# get_tested_value returns the number of flows
class ColumnValuesTest(TcptraceTest):
	def get_tested_value(self, yml):
		a =  self.trace.get(yml["csv"])
		code.interact(local=locals()) 
		return a[:,yml["column"]]

class Checker:
	def check(self):
		is_ok = True
		self.logs=self.test_id+"\n"
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

from mpMptcptraceData import *

# Runs tests based on mptcptrace
# It (in the method inherited from its parent class) instanciates the ...Test class passing it the MptcptraceData instance
class MptcptraceChecker(Checker):
	def __init__(self, yml, test_id, destDir):
		self.yml = yml["mptcptrace"]
		self.trace = MptcptraceData(destDir+"/client.pcap")
		self.test_id = test_id


