from core.experience import Experience, ExperienceParameter
from mpPvAt import MpPvAt
import os

class  ExperienceNetperf(Experience):
	NETPERF_LOG = "netperf.log"
	NETSERVER_LOG = "netserver.log"
	NETPERF_BIN = "netperf"
	NETSERVER_BIN = "netserver"
	PING_OUTPUT = "ping.log"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		Experience.__init__(self, xpParamFile, mpTopo, mpConfig)
		self.loadParam()
		self.ping()
		Experience.classicRun(self)

	def ping(self):
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				ExperienceNetperf.PING_OUTPUT)
		count = self.xpParam.getParam(ExperienceParameter.PINGCOUNT)
		for i in range(0, self.mpConfig.getClientInterfaceCount()):
			 cmd = self.pingCommand(self.mpConfig.getClientIP(i),
				 self.mpConfig.getServerIP(), n = count)
			 self.mpTopo.commandTo(self.mpConfig.client, cmd)

	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				  " >> " + ExperienceNetperf.PING_OUTPUT
		print(s)
		return s

	def loadParam(self):
		"""
		todo : param LD_PRELOAD ??
		"""
		self.testlen = self.xpParam.getParam(ExperienceParameter.NETPERFTESTLEN)
		self.testname = self.xpParam.getParam(ExperienceParameter.NETPERFTESTNAME)
		self.reqres_size = self.xpParam.getParam(ExperienceParameter.NETPERFREQRESSIZE)

	def prepare(self):
		Experience.prepare(self)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " +
				ExperienceNetperf.NETPERF_LOG)
		self.mpTopo.commandTo(self.mpConfig.server, "rm " +
				ExperienceNetperf.NETSERVER_LOG)

	def getClientCmd(self):
		s = ExperienceNetperf.NETPERF_BIN + " -H " + self.mpConfig.getServerIP() + \
			" -l " + self.testlen + " -t " + self.testname + " -- -r " + self.reqres_size + \
			" &>" + ExperienceNetperf.NETPERF_LOG
		print(s)
		return s

	def getServerCmd(self):
		s = "sudo " + ExperienceNetperf.NETSERVER_BIN + " &>" + \
			ExperienceNetperf.NETSERVER_LOG + "&"
		print(s)
		return s

	def clean(self):
		Experience.clean(self)
		#todo use cst
		#self.mpTopo.commandTo(self.mpConfig.server, "killall netcat")


	def run(self):
		cmd = self.getServerCmd()
		self.mpTopo.commandTo(self.mpConfig.server, cmd)

		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
		cmd = self.getClientCmd()
		self.mpTopo.commandTo(self.mpConfig.client, cmd)
		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
