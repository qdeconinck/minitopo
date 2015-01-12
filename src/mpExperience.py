from mpParamXp import MpParamXp

class MpExperience:
	PING = "ping"
	NCPV = "ncpv"
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
		self.mpTopo.commandTo(self.mpConfig.client,
				"killall tcpdump")
		self.mpTopo.commandTo(self.mpConfig.server,
				"killall tcpdump")
		pass

	def runTcpDump(self):
		#todo : replace filename by cst
		if self.xpParam.getParam(MpParamXp.CLIENTPCAP) == "yes" :
			self.mpTopo.commandTo(self.mpConfig.client,
					"tcpdump -i any -w client.pcap &")
		if self.xpParam.getParam(MpParamXp.SERVERPCAP) == "yes" :
			self.mpTopo.commandTo(self.mpConfig.client,
					"tcpdump -i any -w server.pcap &")
		self.mpTopo.commandTo(self.mpConfig.client,
				"sleep 5")
