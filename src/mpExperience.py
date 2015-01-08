from mpParamXp import MpParamXp

class MpExperience:
	PING = "ping"
	def __init__(self, xpParam, mpTopo, mpConfig):
		self.xpParam  = xpParam
		self.mpTopo   = mpTopo
		self.mpConfig = mpConfig
		print(self.xpParam)
	
	def classicRun(self):
		self.prepare()
		self.run()
		self.clean()
	
	def prepare(self):
		self.runTcpDump()
		pass

	def run(self):
		pass

	def clean(self):
		pass

	def runTcpDump(self):
		if self.xpParam.getParam(MpParamXp.CLIENTPCAP) == "yes":
			print("todo : run client dump")
		if self.xpParam.getParam(MpParamXp.SERVERPCAP) == "yes":
			print("todo : run server dump")
