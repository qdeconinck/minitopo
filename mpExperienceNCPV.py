from mpExperience import MpExperience
from mpParamXp import MpParamXp
from mpPvAt import MpPvAt

class  MpExperienceNCPV(MpExperience):
	"""
	NC PV : NetCat and Pipe Viewer
	"""
	SERVER_NC_LOG = "netcat_server"
	CLIENT_NC_LOG = "netcat_client"
	NC_BIN = "/usr/local/bin/nc"
	PV_BIN = "/usr/local/bin/pv"
	PING_OUTPUT = "ping.log"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		MpExperience.__init__(self, xpParamFile, mpTopo, mpConfig)
		self.loadParam()
		self.ping()
		MpExperience.classicRun(self)

	def ping(self):
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				MpExperienceNCPV.PING_OUTPUT )
		count = self.xpParam.getParam(MpParamXp.PINGCOUNT)
		for i in range(0, self.mpConfig.getClientInterfaceCount()):
			 cmd = self.pingCommand(self.mpConfig.getClientIP(i),
				 self.mpConfig.getServerIP(), n = count)
			 self.mpTopo.commandTo(self.mpConfig.client, cmd)

	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				  " >> " + MpExperienceNCPV.PING_OUTPUT
		print(s)
		return s

	def loadParam(self):
		self.pvg = self.xpParam.getParam(MpParamXp.PVG)
		self.pvz = self.xpParam.getParam(MpParamXp.PVZ)
		self.pvRateLimit = self.xpParam.getParam(MpParamXp.PVRATELIMIT)
		self.ddibs = self.xpParam.getParam(MpParamXp.DDIBS)
		self.ddobs = self.xpParam.getParam(MpParamXp.DDOBS)
		self.ddcount = self.xpParam.getParam(MpParamXp.DDCOUNT)
		self.ncServerPort = self.xpParam.getParam(MpParamXp.NCSERVERPORT)
		self.pvRateLimit = self.xpParam.getParam(MpParamXp.PVRATELIMIT)
		self.ncClientPort = []
		for k in sorted(self.xpParam.paramDic):
			if k.startswith(MpParamXp.NCCLIENTPORT):
				port = self.xpParam.paramDic[k]
				self.ncClientPort.append(port)
		if len(self.ncClientPort) == 0:
			d = self.xpParam.getParam(MpParamXp.NCCLIENTPORT)
			self.ncClientPort.append(d)
		self.loadPvAt()

	def loadPvAt(self):
		self.changePvAt = []
		self.changePv = self.xpParam.getParam(MpParamXp.CHANGEPV)
		if self.changePv != "yes":
			print("Don't change pv rate...")
			return
		changePvAt = self.xpParam.getParam(MpParamXp.CHANGEPVAT)
		if not isinstance(changePvAt, list):
			changePvAt = [changePvAt]
		for p in changePvAt:
			tab = p.split(",")
			if len(tab)==2:
				o = MpPvAt(float(tab[0]), tab[1])
				self.addPvAt(o)
			else:
				print("pv wrong line : " + n)

	def addPvAt(self, p):
		if len(self.changePvAt) == 0 :
			p.delta = p.at
		else:
			if p.at > self.changePvAt[-1].at:
				p.delta = p.at - self.changePvAt[-1].at
			else:
				print("Do not take into account " + p.__str__() + \
						"because ooo !")
				return

		self.changePvAt.append(p)

	def getPvChangeCmd(self):
		cmd = ""
		for p in self.changePvAt:
			cmd = cmd + "sleep " + str(p.delta)
			cmd = cmd + " && "
			cmd = cmd + MpExperienceNCPV.PV_BIN + " -R " + self.pvPid
			cmd = cmd + " " + p.cmd + " && "
		cmd = cmd + " true &"
		return cmd

	def prepare(self):
		MpExperience.prepare(self)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				MpExperienceNCPV.CLIENT_NC_LOG )
		self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
				MpExperienceNCPV.SERVER_NC_LOG )

	def getNCServerCmd(self, id):
		s = MpExperienceNCPV.NC_BIN + " -d  " + \
				" -l " + self.ncServerPort  + \
				" 1>/dev/null 2>" + MpExperienceNCPV.SERVER_NC_LOG + \
				"_" + str(id) + ".log &"
		print(s)
		return s

	def getNCClientCmd(self, id):
		s = "dd if=/dev/urandom ibs=" + self.ddibs + \
				" obs=" + self.ddobs + \
				" count=" + self.ddcount + \
				" | " + MpExperienceNCPV.PV_BIN + \
				" -g " + self.pvg + " -z " + self.pvz + \
				" -q --rate-limit " + self.pvRateLimit + \
				" | " + MpExperienceNCPV.NC_BIN + " " + \
				"  -p " + self.ncClientPort[id] + " " + \
				self.mpConfig.getServerIP() + " " + \
				self.ncServerPort + " " + \
				"&>" + MpExperienceNCPV.CLIENT_NC_LOG + \
				"_" + str(id) + ".log"
		print(s)
		return s
	def getPvPidCmd(self):
		s = "pgrep -n pv"
		return s

	def clean(self):
		MpExperience.clean(self)
		#todo use cst
		self.mpTopo.commandTo(self.mpConfig.server, "killall netcat")


	def run(self):
		for i in range(0, len(self.ncClientPort)):
			cmd = self.getNCServerCmd(i)
			self.mpTopo.commandTo(self.mpConfig.server, cmd)

			cmd = self.getNCClientCmd(i)
			self.mpConfig.client.sendCmd(cmd)

			cmd = self.getPvPidCmd()
			self.pvPid = None
			while self.pvPid == None or self.pvPid == "": 
				self.pvPid = self.mpTopo.commandTo(self.mpConfig.server, cmd)[:-1]
				print("guessing pv pid ... :" + str(self.pvPid))

			cmd = self.getPvChangeCmd()
			print(cmd)
			self.mpTopo.commandTo(self.mpConfig.server, cmd)


			self.mpConfig.client.waitOutput()

			self.mpTopo.commandTo(self.mpConfig.client, "sleep 1")

