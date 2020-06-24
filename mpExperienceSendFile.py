from core.experience import Experience, ExperienceParameter
from mpPvAt import MpPvAt
import os

class  ExperienceSendFile(Experience):
	SERVER_LOG = "sendfile_server.log"
	CLIENT_LOG = "sendfile_client.log"
	WGET_BIN = "./client"
	PING_OUTPUT = "ping.log"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		Experience.__init__(self, xpParamFile, mpTopo, mpConfig)
		self.loadParam()
		self.ping()
		Experience.classicRun(self)

	def ping(self):
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				ExperienceSendFile.PING_OUTPUT )
		count = self.xpParam.getParam(ExperienceParameter.PINGCOUNT)
		for i in range(0, self.mpConfig.getClientInterfaceCount()):
			 cmd = self.pingCommand(self.mpConfig.getClientIP(i),
				 self.mpConfig.getServerIP(), n = count)
			 self.mpTopo.commandTo(self.mpConfig.client, cmd)

	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				  " >> " + ExperienceSendFile.PING_OUTPUT
		print(s)
		return s

	def loadParam(self):
		"""
		todo : param LD_PRELOAD ??
		"""
		self.file = self.xpParam.getParam(ExperienceParameter.HTTPSFILE)
		self.random_size = self.xpParam.getParam(ExperienceParameter.HTTPSRANDOMSIZE)

	def prepare(self):
		Experience.prepare(self)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				ExperienceSendFile.CLIENT_LOG )
		self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
				ExperienceSendFile.SERVER_LOG )
		if self.file  == "random":
			self.mpTopo.commandTo(self.mpConfig.client,
				"dd if=/dev/urandom of=random bs=1K count=" + \
				self.random_size)

	def getSendFileServerCmd(self):
		s = "./server &>" + ExperienceSendFile.SERVER_LOG + "&"
		print(s)
		return s

	def getSendFileClientCmd(self):
		s = ExperienceSendFile.WGET_BIN + " " + self.mpConfig.getServerIP() + " &>" + ExperienceSendFile.CLIENT_LOG
		print(s)
		return s

	def clean(self):
		Experience.clean(self)
		if self.file  == "random":
			self.mpTopo.commandTo(self.mpConfig.client, "rm random*")
		#todo use cst
		#self.mpTopo.commandTo(self.mpConfig.server, "killall netcat")


	def run(self):
		cmd = self.getSendFileServerCmd()
		self.mpTopo.commandTo(self.mpConfig.server, cmd)

		self.mpTopo.commandTo(self.mpConfig.client, "sleep 0.1")
		cmd = self.getSendFileClientCmd()
		self.mpTopo.commandTo(self.mpConfig.client, cmd)
		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
