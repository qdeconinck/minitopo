from mpParamXp import MpParamXp
from mpMultiInterfaceTopo import MpMultiInterfaceTopo

class MpExperience:
	PING = "ping"
	NCPV = "ncpv"
	NC = "nc"
	NONE = "none"
	HTTPS = "https"
	HTTP = "http"
	EPLOAD = "epload"
	NETPERF = "netperf"
	AB = "ab"
	SIRI = "siri"
	SENDFILE = "sendfile"
	VLC = "vlc"
	IPERF = "iperf"
	DITG = "ditg"
	MSG = "msg"

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
		self.runUserspacePM()
		self.mpConfig.configureNetwork()
		self.changeMetric()
		self.putPriorityOnPaths()
		self.runTcpDump()
		self.runNetemAt()
		pass

	def changeMetric(self):
		metric = self.xpParam.getParam(MpParamXp.METRIC)
		if int(metric) >= 0:
			self.mpTopo.notNSCommand("echo " + metric + " > /sys/module/mptcp_sched_metric/parameters/metric")

	def putPriorityOnPaths(self):
		# Only meaningful if mpTopo is instance of MpMultiInterfaceTopo
		if isinstance(self.mpTopo, MpMultiInterfaceTopo):
			prioPath0 = self.xpParam.getParam(MpParamXp.PRIOPATH0)
			prioPath1 = self.xpParam.getParam(MpParamXp.PRIOPATH1)
			if not prioPath0 == prioPath1:
				self.mpTopo.commandTo(self.mpConfig.client, "/home/mininet/iproute/ip/ip link set dev " +
						  			  self.mpConfig.getClientInterface(0) + " priority " + str(prioPath0))
				self.mpTopo.commandTo(self.mpConfig.router, "/home/mininet/iproute/ip/ip link set dev " +
									  self.mpConfig.getRouterInterfaceSwitch(0) + " priority " +
									  str(prioPath0))
				self.mpTopo.commandTo(self.mpConfig.client, "/home/mininet/iproute/ip/ip link set dev " +
									  self.mpConfig.getClientInterface(1) + " priority " + str(prioPath1))
				self.mpTopo.commandTo(self.mpConfig.router, "/home/mininet/iproute/ip/ip link set dev " +
									  self.mpConfig.getRouterInterfaceSwitch(1) + " priority " +
									  str(prioPath1))

			backupPath0 = self.xpParam.getParam(MpParamXp.BACKUPPATH0)
			if int(backupPath0) > 0:
				self.mpTopo.commandTo(self.mpConfig.client, self.mpConfig.interfaceBUPCommand(self.mpConfig.getClientInterface(0)))
				self.mpTopo.commandTo(self.mpConfig.router, self.mpConfig.interfaceBUPCommand(self.mpConfig.getRouterInterfaceSwitch(0)))
			backupPath1 = self.xpParam.getParam(MpParamXp.BACKUPPATH1)
			if int(backupPath1) > 0:
				self.mpTopo.commandTo(self.mpConfig.client, self.mpConfig.interfaceBUPCommand(self.mpConfig.getClientInterface(1)))
				self.mpTopo.commandTo(self.mpConfig.router, self.mpConfig.interfaceBUPCommand(self.mpConfig.getRouterInterfaceSwitch(1)))

	def runUserspacePM(self):
		if self.xpParam.getParam(MpParamXp.KERNELPMC) != "netlink":
			print("Client : Error, I can't change the userspace pm if the kernel pm is not netlink !")
		else:
			upmc = self.xpParam.getParam(MpParamXp.USERPMC)
			upmca = self.xpParam.getParam(MpParamXp.USERPMCARGS)
			self.mpTopo.commandTo(self.mpConfig.client, upmc + \
					" " + upmca + " &>upmc.log &")
		if self.xpParam.getParam(MpParamXp.KERNELPMS) != "netlink":
			print("Server : Error, I can't change the userspace pm if the kernel pm is not netlink !")
		else:
			upms = self.xpParam.getParam(MpParamXp.USERPMS)
			upmsa = self.xpParam.getParam(MpParamXp.USERPMSARGS)
			self.mpTopo.commandTo(self.mpConfig.server, upms + \
					" " + upmsa + " &>upms.log &")

	def cleanUserspacePM(self):
		if self.xpParam.getParam(MpParamXp.KERNELPMC) != "netlink":
			print("Client : Error, I can't change the userspace pm if the kernel pm is not netlink !")
		else:
			upmc = self.xpParam.getParam(MpParamXp.USERPMC)
			self.mpTopo.commandTo(self.mpConfig.client, "killall " + upmc)
		if self.xpParam.getParam(MpParamXp.KERNELPMS) != "netlink":
			print("Server : Error, I can't change the userspace pm if the kernel pm is not netlink !")
		else:
			upms = self.xpParam.getParam(MpParamXp.USERPMS)
			self.mpTopo.commandTo(self.mpConfig.server, "killall " + upms)

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
		self.cleanUserspacePM()
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
