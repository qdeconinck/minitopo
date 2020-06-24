from core.experience import Experience, ExperienceParameter
from mpPvAt import MpPvAt
import os

class ExperienceHTTPS(Experience):
	SERVER_LOG = "https_server.log"
	CLIENT_LOG = "https_client.log"
	WGET_BIN = "wget"
	PING_OUTPUT = "ping.log"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		Experience.__init__(self, xpParamFile, mpTopo, mpConfig)
		self.loadParam()
		self.ping()
		Experience.classicRun(self)

	def ping(self):
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				ExperienceHTTPS.PING_OUTPUT )
		count = self.xpParam.getParam(ExperienceParameter.PINGCOUNT)
		for i in range(0, self.mpConfig.getClientInterfaceCount()):
			 cmd = self.pingCommand(self.mpConfig.getClientIP(i),
				 self.mpConfig.getServerIP(), n = count)
			 self.mpTopo.commandTo(self.mpConfig.client, cmd)

	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				  " >> " + ExperienceHTTPS.PING_OUTPUT
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
				ExperienceHTTPS.CLIENT_LOG )
		self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
				ExperienceHTTPS.SERVER_LOG )
		if self.file  == "random":
			self.mpTopo.commandTo(self.mpConfig.client,
				"dd if=/dev/urandom of=random bs=1K count=" + \
				self.random_size)

	def getHTTPSServerCmd(self):
		s = "python " + os.path.dirname(os.path.abspath(__file__))  + \
				"/https.py &>" + ExperienceHTTPS.SERVER_LOG + "&"
		print(s)
		return s

	def getHTTPSClientCmd(self):
		s = "(time " +ExperienceHTTPS.WGET_BIN + " https://" + self.mpConfig.getServerIP() + \
				"/" + self.file + " --no-check-certificate) &>" + ExperienceHTTPS.CLIENT_LOG
		print(s)
		return s

	def clean(self):
		Experience.clean(self)
		if self.file  == "random":
			self.mpTopo.commandTo(self.mpConfig.client, "rm random*")
		#todo use cst
		#self.mpTopo.commandTo(self.mpConfig.server, "killall netcat")


	def run(self):
		cmd = self.getHTTPSServerCmd()
		self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_before")
		self.mpTopo.commandTo(self.mpConfig.server, cmd)

		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
		cmd = self.getHTTPSClientCmd()
		self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_before")
		self.mpTopo.commandTo(self.mpConfig.client, cmd)
		self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_after")
		self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_after")
		self.mpTopo.commandTo(self.mpConfig.server, "pkill -f https.py")
		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
