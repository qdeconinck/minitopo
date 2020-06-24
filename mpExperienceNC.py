from core.experience import Experience, ExperienceParameter

"""
Should be the mother of ExperienceNCPV, shame on me, should rewrite
ExperienceNCPV as daughter class of this one.
"""

class  ExperienceNC(Experience): 
	SERVER_NC_LOG = "netcat_server"
	CLIENT_NC_LOG = "netcat_client"
	NC_BIN = "netcat"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		Experience.__init__(self, xpParamFile, mpTopo, mpConfig)
		self.loadParam()
		Experience.classicRun(self)
	
	def loadParam(self):
		self.ddibs = self.xpParam.getParam(ExperienceParameter.DDIBS)
		self.ddobs = self.xpParam.getParam(ExperienceParameter.DDOBS)
		self.ddcount = self.xpParam.getParam(ExperienceParameter.DDCOUNT)
		self.ncServerPort = self.xpParam.getParam(ExperienceParameter.NCSERVERPORT)
		self.ncClientPort = []
		for k in sorted(self.xpParam.paramDic):
			if k.startswith(ExperienceParameter.NCCLIENTPORT):
				port = self.xpParam.paramDic[k]
				self.ncClientPort.append(port)
		if len(self.ncClientPort) == 0:
			d = self.xpParam.getParam(ExperienceParameter.NCCLIENTPORT)
			self.ncClientPort.append(d)

	def prepare(self):
		Experience.prepare(self)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				ExperienceNC.CLIENT_NC_LOG )
		self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
				ExperienceNC.SERVER_NC_LOG )

	def getNCServerCmd(self, id):
		s = "dd if=/dev/urandom ibs=" + self.ddibs + \
				" obs=" + self.ddobs + \
				" count=" + self.ddcount + \
				" | " + \
				ExperienceNC.NC_BIN + \
				" -l " + self.ncServerPort  + \
				" &>" + ExperienceNC.SERVER_NC_LOG + \
				"_" + str(id) + ".log"
		print(s)
		return s

	def getNCClientCmd(self, id):
		s = ExperienceNC.NC_BIN + " " + \
				" -p " + self.ncClientPort[id] + " " + \
				self.mpConfig.getServerIP() + " " + \
				self.ncServerPort + " " + \
				"&>" + ExperienceNC.CLIENT_NC_LOG + \
				"_" + str(id) + ".log"
		print(s)
		return s

	def clean(self):
		Experience.clean(self)
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

