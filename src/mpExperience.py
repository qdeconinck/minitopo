from mpParamXp import MpParamXp

class MpExperience:
	NONE = "none"
	HTTPS = "https"
	QUIC = "quic"
	QUICREQRES = "quicreqres"

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
		self.mpConfig.configureNetwork()
		self.disableTSO()
		self.runTcpDump()
		self.runNetemAt()
		pass

	def disableTSO(self):
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
			cmd = "ethtool -K " + lif + " tso off"
			print(cmd)
			self.mpTopo.commandTo(lbox, cmd)
			cmd = "ethtool -K " + rif + " tso off"
			print(cmd)
			self.mpTopo.commandTo(rbox, cmd)
			i = i + 1

		# And for the server
		cmd = "ethtool -K " + self.mpConfig.getServerInterface() + " tso off"
		print(cmd)
		self.mpTopo.commandTo(self.mpConfig.server, cmd)

		cmd = "ethtool -K " + self.mpConfig.getRouterInterfaceSwitch(self.mpConfig.getClientInterfaceCount()) + " tso off"
		print(cmd)
		self.mpTopo.commandTo(self.mpConfig.router, cmd)

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
		self._saveSysctl(MpParamXp.sysctlKey, self.sysctlBUP)
		self.sysctlBUPC = {}
		self._saveSysctl(MpParamXp.sysctlKeyClient, self.sysctlBUPC,
				ns = True, who = self.mpConfig.client)
		self.sysctlBUPS = {}
		self._saveSysctl(MpParamXp.sysctlKeyServer, self.sysctlBUPS,
				ns = True, who = self.mpConfig.server)

	def _saveSysctl(self, sysctlDic, sysctlBUP, ns = False, who = None):
		for k in sysctlDic:
			sysctlKey = sysctlDic[k]
			cmd = self.cmdReadSysctl(sysctlKey)
			if not ns:
				val = self.mpTopo.notNSCommand(cmd)
			else:
				val = self.mpTopo.commandTo(who, cmd)
			if val == "Error":
				print("oooops can't get sysctl " + sysctlKey)
			else:
				sysctlBUP[k] = val.split(" ",2)[2][:-1]


	def cmdReadSysctl(self, key):
		s = "sysctl " + key
		return s

	def cmdWriteSysctl(self, key, value):
		s = self.cmdReadSysctl(key)
		s = s + "=\"" + str(value) + "\""
		return s

	def writeSysctl(self):
		self._writeSysctl(MpParamXp.sysctlKey, self.sysctlBUP)
		self._writeSysctl(MpParamXp.sysctlKeyClient, self.sysctlBUPC,
				ns = True, who = self.mpConfig.client)
		self._writeSysctl(MpParamXp.sysctlKeyServer, self.sysctlBUPS,
				ns = True, who = self.mpConfig.server)

	def _writeSysctl(self, sysctlDic, sysctlBUP, ns = False, who = None):
		for k in sysctlBUP:
			sysctlKey = sysctlDic[k]
			sysctlValue = self.xpParam.getParam(k)
			cmd = self.cmdWriteSysctl(sysctlKey,sysctlValue)
			if not ns:
				val = self.mpTopo.notNSCommand(cmd)
			else:
				val = self.mpTopo.commandTo(who, cmd)
			if val == "Error":
				print("oooops can't set sysctl " + sysctlKey)


	def backUpSysctl(self):
		self._backUpSysctl(MpParamXp.sysctlKey, self.sysctlBUP)
		self._backUpSysctl(MpParamXp.sysctlKeyClient, self.sysctlBUPC,
				ns = True, who = self.mpConfig.client)
		self._backUpSysctl(MpParamXp.sysctlKeyServer, self.sysctlBUPS,
				ns = True, who = self.mpConfig.server)


	def _backUpSysctl(self, sysctlDic, sysctlBUP, ns = False, who = None):
		for k in sysctlBUP:
			sysctlKey = sysctlDic[k]
			sysctlValue = sysctlBUP[k]
			cmd = self.cmdWriteSysctl(sysctlKey,sysctlValue)
			if not ns:
				val = self.mpTopo.notNSCommand(cmd)
			else:
				val = self.mpTopo.commandTo(who, cmd)

			if val == "Error":
				print("oooops can't set sysctl " + sysctlKey)


	def runTcpDump(self):
		#todo : replace filename by cst
		cpcap = self.xpParam.getParam(MpParamXp.CLIENTPCAP)
		spcap = self.xpParam.getParam(MpParamXp.SERVERPCAP)
		snaplenpcap = self.xpParam.getParam(MpParamXp.SNAPLENPCAP)
		if cpcap == "yes" :
			self.mpTopo.commandTo(self.mpConfig.client,
					"tcpdump -i any -s " + snaplenpcap + " -w client.pcap &")
		if spcap == "yes" :
			self.mpTopo.commandTo(self.mpConfig.server,
					"tcpdump -i any -s " + snaplenpcap + " -w server.pcap &")
		if spcap == "yes" or cpcap == "yes":
			self.mpTopo.commandTo(self.mpConfig.client,"sleep 5")
