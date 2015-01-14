from mpExperience import MpExperience
from mpParamXp import MpParamXp

class  MpExperienceNCPV(MpExperience): 
	"""
	NC PV : NetCat and Pipe Viewer
	"""
	SERVER_NC_LOG = "netcat_server"
	CLIENT_NC_LOG = "netcat_client"
	NC_BIN = "netcat"
	PV_BIN = "/home/bhesmans/Documents/git/pv/pv"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		MpExperience.__init__(self, xpParamFile, mpTopo, mpConfig)
		self.loadParam()
		MpExperience.classicRun(self)
	
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


	def prepare(self):
		MpExperience.prepare(self)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				MpExperienceNCPV.CLIENT_NC_LOG )
		self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
				MpExperienceNCPV.SERVER_NC_LOG )

	def getNCServerCmd(self, id):
		s = MpExperienceNCPV.NC_BIN + " -d " + \
				" -l " + self.ncServerPort  + \
				" &>" + MpExperienceNCPV.SERVER_NC_LOG + \
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
				" -p " + self.ncClientPort[id] + " " + \
				self.mpConfig.getServerIP() + " " + \
				self.ncServerPort + " " + \
				"&>" + MpExperienceNCPV.CLIENT_NC_LOG + \
				"_" + str(id) + ".log"
		print(s)
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
			self.mpTopo.commandTo(self.mpConfig.client, cmd)
			self.mpTopo.commandTo(self.mpConfig.client, "sleep 1")

