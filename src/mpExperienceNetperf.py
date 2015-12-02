from mpExperience import MpExperience
from mpParamXp import MpParamXp
from mpPvAt import MpPvAt
import os

class  MpExperienceNetperf(MpExperience):
	NETPERF_LOG = "netperf.log"
	NETSERVER_LOG = "netserver.log"
	NETPERF_BIN = "netperf"
	NETSERVER_BIN = "netserver"
	PING_OUTPUT = "ping.log"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		MpExperience.__init__(self, xpParamFile, mpTopo, mpConfig)
		self.loadParam()
		self.ping()
		MpExperience.classicRun(self)

	def ping(self):
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				MpExperienceNetperf.PING_OUTPUT)
		count = self.xpParam.getParam(MpParamXp.PINGCOUNT)
		for i in range(0, self.mpConfig.getClientInterfaceCount()):
			 cmd = self.pingCommand(self.mpConfig.getClientIP(i),
				 self.mpConfig.getServerIP(), n = count)
			 self.mpTopo.commandTo(self.mpConfig.client, cmd)

	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				  " >> " + MpExperienceNetperf.PING_OUTPUT
		print(s)
		return s

	def loadParam(self):
		"""
		todo : param LD_PRELOAD ??
		"""
		self.testlen = self.xpParam.getParam(MpParamXp.NETPERFTESTLEN)
		self.testname = self.xpParam.getParam(MpParamXp.NETPERFTESTNAME)
		self.reqres_size = self.XpParam.getParam(MpParamXp.NETPERFREQRESSIZE)

	def prepare(self):
		MpExperience.prepare(self)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " +
				MpExperienceNetperf.NETPERF_LOG)
		self.mpTopo.commandTo(self.mpConfig.server, "rm " +
				MpExperienceNetperf.NETSERVER_LOG)

	def getClientCmd(self):
		s = MpExperienceNetperf.NETPERF_BIN + " -H " + self.mpConfig.getServerIP() + \
			" -l " + self.testlen + " -t " + self.testname + " -r " + self.reqres_size + \
			" &>" + MpExperienceNetperf.NETPERF_LOG
		print(s)
		return s

	def getServerCmd(self):
		s = "sudo " + MpExperienceNetperf.NETSERVER_BIN + " &>" + \
			MpExperienceNetperf.NETSERVER_LOG + "&"
		print(s)
		return s

	def clean(self):
		MpExperience.clean(self)
		#todo use cst
		#self.mpTopo.commandTo(self.mpConfig.server, "killall netcat")


	def run(self):
		cmd = self.getServerCmd()
		self.mpTopo.commandTo(self.mpConfig.server, cmd)

		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
		cmd = self.getClientCmd()
		self.mpTopo.commandTo(self.mpConfig.client, cmd)
		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
