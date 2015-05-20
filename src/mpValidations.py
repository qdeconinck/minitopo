

from mpTcptraceData import *


# A checker runs tests, and a test is made of multiple validations


# For a validation, the value to compare to is the target value from the yaml
# The validation takes place in the validate method, which takes
# as argument a value from which to extract the value to compare or the value itself
class Validation:
	def __init__(self, yml):
		self.compared=yml["target"]
	def name(self):
		return self.__class__.__name__

# checks a value passed is greater or equal (generic)
class MinValueValidation(Validation):
	def validate(self, value):
		return self.compared<=value

# individual flow validation (specific)
# gets flow_spec = (index, flows) where index is the index of the flow to validate, and flows is the array of flows
class MinDelayValidation(Validation):
	def validate(self, flow_spec):
		(index,flows) = flow_spec
		val = float(flows[index][5])-float(flows[0][5])
		return self.compared<=val



# Base class testing tcptrace results
# the inheriting class should implement get_tested_value(self, yml)
# The validate method iterates one the validations mentioned for the test in the yml file.
class TcptraceTest: 
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
			if tester.validate(tested_value):
				self.logs=self.logs+ ("" if self.logs=="" else "\n ")+ "  -" +tester.name()+" OK\n"
				return True
			else:
				self.logs=self.logs+ ("" if self.logs=="" else "\n ")+ "  -" +tester.name()+" FAILS\n"
				is_ok = False
		return is_ok
	def name(self):
		return self.__class__.__name__ 

# get_tested_value returns the number of flows
class NumberOfFlowsTest(TcptraceTest):
	def get_tested_value(self, yml):
		return self.trace.number_of_flows

# get_tested_value returns index of the flow to validate, and the list of flows
class FlowsTest(TcptraceTest):
	def get_tested_value(self, yml):
		return (yml["index"],self.trace.flows) 


# Runs tests based on tcptrace
class TcptraceChecker:
	def __init__(self, yml, test_id):
		self.yml = yml["tcptrace"]
		self.trace = TcptraceData("/tmp/dest/client.pcap")
		self.test_id = test_id
	def check(self):
		is_ok = True
		self.logs=self.test_id+"\n"
		for test in self.yml:
			name=test["test"].title().replace("_","")+"Test"
			klass = globals()[name]
			r = klass(test, self.trace)
			if r.validate():
				self.logs = self.logs + " *" + r.name() + " SUCCESS\n"
				self.logs = self.logs +  r.logs
			else:
				self.logs = self.logs + " *" + self.test_id + " " + r.name() + " FAIL\n"
				self.logs = self.logs + r.logs


