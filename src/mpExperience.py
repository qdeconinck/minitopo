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
		self.setupSysctl()
		self.runTcpDump()
		self.runNetemAt()
		pass

	def runNetemAt(self):
		if not self.mpTopo.changeNetem == "yes":
			print("I don't need to change netem")
			return
		print("Will change netem config on the fly")
		links = self.mpTopo.getLinkCharacteristics()
		i = 0
		for l in links:
			lname = self.mpConfig.getMidLeftName(i)
			rname = self.mpConfig.getMidRightName(i)
			lbox = self.mpTopo.getHost(lname)
			lif = self.mpConfig.getMidL2RInterface(i)
			rif = self.mpConfig.getMidR2LInterface(i)
			rbox = self.mpTopo.getHost(rname)
			print(str(lname) + " " + str(lif))
			print(str(rname) + " " + str(rif))
			print("boxes " + str(lbox) + " " + str(rbox))
			cmd = l.buildNetemCmd(lif)
			print(cmd)
			self.mpTopo.commandTo(lbox, cmd)
			cmd = l.buildNetemCmd(rif)
			print(cmd)
			self.mpTopo.commandTo(rbox, cmd)
			i = i + 1

	def run(self):
		pass

	def clean(self):
		self.mpTopo.commandTo(self.mpConfig.client,
				"killall tcpdump")
		self.mpTopo.commandTo(self.mpConfig.server,
				"killall tcpdump")
		self.backUpSysctl()
		pass

	def setupSysctl(self):
		self.saveSysctl()
		self.writeSysctl()

	def saveSysctl(self):
		self.sysctlBUP = {}
		for k in MpParamXp.sysctlKey:
			sysctlKey = MpParamXp.sysctlKey[k]
			cmd = self.cmdReadSysctl(sysctlKey)
			val = self.mpTopo.notNSCommand(cmd)
			if val == "Error":
				print("oooops can't get sysctl " + sysctlKey)
			else:
				self.sysctlBUP[k] = val.split(" ",2)[2][:-1]

	def cmdReadSysctl(self, key):
		s = "sysctl " + key
		return s

	def cmdWriteSysctl(self, key, value):
		s = self.cmdReadSysctl(key)
		s = s + "=\"" + str(value) + "\""
		return s

	def writeSysctl(self):
		for k in self.sysctlBUP:
			sysctlKey = MpParamXp.sysctlKey[k]
			sysctlValue = self.xpParam.getParam(k)
			cmd = self.cmdWriteSysctl(sysctlKey,sysctlValue)
			val = self.mpTopo.notNSCommand(cmd)
			if val == "Error":
				print("oooops can't set sysctl " + sysctlKey)

	def backUpSysctl(self):
		for k in self.sysctlBUP:
			sysctlKey = MpParamXp.sysctlKey[k]
			sysctlValue = self.sysctlBUP[k]
			cmd = self.cmdWriteSysctl(sysctlKey,sysctlValue)
			val = self.mpTopo.notNSCommand(cmd)
			if val == "Error":
				print("oooops can't set sysctl " + sysctlKey)

	def runTcpDump(self):
		#todo : replace filename by cst
		cpcap = self.xpParam.getParam(MpParamXp.CLIENTPCAP)
		spcap = self.xpParam.getParam(MpParamXp.SERVERPCAP)
		if cpcap == "yes" :
			self.mpTopo.commandTo(self.mpConfig.client,
					"tcpdump -i any -w client.pcap &")
		if spcap == "yes" :
			self.mpTopo.commandTo(self.mpConfig.client,
					"tcpdump -i any -w server.pcap &")
		if spcap == "yes" or cpcap == "yes":
			self.mpTopo.commandTo(self.mpConfig.client,"sleep 5")
