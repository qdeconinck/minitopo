from mpExperience import MpExperience
from mpParamXp import MpParamXp
from mpPvAt import MpPvAt
import os

class MpExperienceIperf(MpExperience):
	IPERF_LOG = "iperf.log"
	SERVER_LOG = "server.log"
	IPERF_BIN = "iperf3"
	PING_OUTPUT = "ping.log"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		MpExperience.__init__(self, xpParamFile, mpTopo, mpConfig)
		self.loadParam()
		self.ping()
		MpExperience.classicRun(self)

	def ping(self):
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				MpExperienceIperf.PING_OUTPUT)
		count = self.xpParam.getParam(MpParamXp.PINGCOUNT)
		for i in range(0, self.mpConfig.getClientInterfaceCount()):
			 cmd = self.pingCommand(self.mpConfig.getClientIP(i),
				 self.mpConfig.getServerIP(), n = count)
			 self.mpTopo.commandTo(self.mpConfig.client, cmd)

	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				  " >> " + MpExperienceIperf.PING_OUTPUT
		print(s)
		return s

	def loadParam(self):
		"""
		todo : param LD_PRELOAD ??
		"""
		pass

	def prepare(self):
		MpExperience.prepare(self)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " +
				MpExperienceIperf.IPERF_LOG)
		self.mpTopo.commandTo(self.mpConfig.server, "rm " +
				MpExperienceIperf.SERVER_LOG)

	def getClientCmd(self):
		s = MpExperienceIperf.IPERF_BIN + " -c " + self.mpConfig.getServerIP() + \
			" -t 10 -w " + str(int(self.xpParam.getParam(MpParamXp.RMEM).split()[-1]) / 1000) + "K -l " + str(int(self.xpParam.getParam(MpParamXp.RMEM).split()[-1]) / 1000) + "K &>" + MpExperienceIperf.IPERF_LOG
		print(s)
		return s

	def getServerCmd(self):
		s = "sudo " + MpExperienceIperf.IPERF_BIN + " -s -w " + str(int(self.xpParam.getParam(MpParamXp.RMEM).split()[-1]) / 1000) + "K -l " + str(int(self.xpParam.getParam(MpParamXp.RMEM).split()[-1]) / 1000) + "K &>" + \
			MpExperienceIperf.SERVER_LOG + "&"
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
		self.mpTopo.commandTo(self.mpConfig.server, "pkill -9 -f iperf")
		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
