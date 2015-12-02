from mpExperience import MpExperience
from mpParamXp import MpParamXp
from mpPvAt import MpPvAt
import os

class  MpExperienceAb(MpExperience):
	SERVER_LOG = "ab_server.log"
	CLIENT_LOG = "ab_client.log"
	AB_BIN = "ab"
	PING_OUTPUT = "ping.log"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		MpExperience.__init__(self, xpParamFile, mpTopo, mpConfig)
		self.loadParam()
		self.ping()
		MpExperience.classicRun(self)

	def ping(self):
		self.mpTopo.commandTo(self.mpConfig.client,
						"rm " + MpExperienceAb.PING_OUTPUT)
		count = self.xpParam.getParam(MpParamXp.PINGCOUNT)
		for i in range(0, self.mpConfig.getClientInterfaceCount()):
			 cmd = self.pingCommand(self.mpConfig.getClientIP(i),
				 self.mpConfig.getServerIP(), n = count)
			 self.mpTopo.commandTo(self.mpConfig.client, cmd)

	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				  " >> " + MpExperienceAb.PING_OUTPUT
		print(s)
		return s

	def loadParam(self):
		"""
		todo : param LD_PRELOAD ??
		"""
		self.file = self.xpParam.getParam(MpParamXp.HTTPFILE)
		self.random_size = self.xpParam.getParam(MpParamXp.HTTPRANDOMSIZE)
		self.concurrent_requests = self.xpParam.getParam(MpParamXp.ABCONCURRENTREQUESTS)
		self.timelimit = self.xpParam.getParam(MpParamXp.ABTIMELIMIT)

	def prepare(self):
		MpExperience.prepare(self)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				MpExperienceAb.CLIENT_LOG )
		self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
				MpExperienceAb.SERVER_LOG )
		if self.file  == "random":
			self.mpTopo.commandTo(self.mpConfig.client,
				"dd if=/dev/urandom of=random bs=1K count=" + \
				self.random_size)

	def getAbServerCmd(self):
		s = "python " + os.path.dirname(os.path.abspath(__file__))  + \
				"/http.py &>" + MpExperienceAb.SERVER_LOG + "&"
		print(s)
		return s

	def getAbClientCmd(self):
		s = MpExperienceAb.AB_BIN + " -c " + self.concurrent_requests + " -t " + \
		 	self.timelimit + " http://" + self.mpConfig.getServerIP() + "/" + self.file + \
			" &>" + MpExperienceAb.CLIENT_LOG
		print(s)
		return s

	def clean(self):
		MpExperience.clean(self)
		if self.file  == "random":
			self.mpTopo.commandTo(self.mpConfig.client, "rm random*")
		#todo use cst
		#self.mpTopo.commandTo(self.mpConfig.server, "killall netcat")


	def run(self):
		cmd = self.getAbServerCmd()
		self.mpTopo.commandTo(self.mpConfig.server, cmd)

		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
		cmd = self.getAbClientCmd()
		self.mpTopo.commandTo(self.mpConfig.client, cmd)
		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
