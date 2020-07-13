from mpExperience import MpExperience
from mpParamXp import MpParamXp
from mpPvAt import MpPvAt

"""
Should be the mother of MpExperienceNCPV, shame on me, should rewrite
MpExperienceNCPV as daughter class of this one.
"""

class  MpExperienceNC(MpExperience): 
	SERVER_NC_LOG = "netcat_server"
	CLIENT_NC_LOG = "netcat_client"
	NC_BIN = "netcat"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		MpExperience.__init__(self, xpParamFile, mpTopo, mpConfig)
		self.loadParam()
		MpExperience.classicRun(self)
	
	def loadParam(self):
		self.ddibs = self.xpParam.getParam(MpParamXp.DDIBS)
		self.ddobs = self.xpParam.getParam(MpParamXp.DDOBS)
		self.ddcount = self.xpParam.getParam(MpParamXp.DDCOUNT)
		self.ncServerPort = self.xpParam.getParam(MpParamXp.NCSERVERPORT)
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
				MpExperienceNC.CLIENT_NC_LOG )
		self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
				MpExperienceNC.SERVER_NC_LOG )

	def getNCServerCmd(self, id):
		s = "dd if=/dev/urandom ibs=" + self.ddibs + \
				" obs=" + self.ddobs + \
				" count=" + self.ddcount + \
				" | " + \
				MpExperienceNC.NC_BIN + \
				" -l " + self.ncServerPort  + \
				" &>" + MpExperienceNC.SERVER_NC_LOG + \
				"_" + str(id) + ".log"
		print(s)
		return s

	def getNCClientCmd(self, id):
		s = MpExperienceNC.NC_BIN + " " + \
				" -p " + self.ncClientPort[id] + " " + \
				self.mpConfig.getServerIP() + " " + \
				self.ncServerPort + " " + \
				"&>" + MpExperienceNC.CLIENT_NC_LOG + \
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
			self.mpConfig.server.sendCmd(cmd)
			
			cmd = self.getNCClientCmd(i)
			self.mpTopo.commandTo(self.mpConfig.client, cmd)

			self.mpConfig.server.waitOutput()
			
			self.mpTopo.commandTo(self.mpConfig.client, "sleep 1")

