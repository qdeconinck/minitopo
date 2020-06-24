from core.experience import Experience, ExperienceParameter
import os

class ExperienceIperf(Experience):
	IPERF_LOG = "iperf.log"
	SERVER_LOG = "server.log"
	IPERF_BIN = "iperf3"
	PING_OUTPUT = "ping.log"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		Experience.__init__(self, xpParamFile, mpTopo, mpConfig)
		self.loadParam()
		self.ping()
		Experience.classicRun(self)

	def ping(self):
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				ExperienceIperf.PING_OUTPUT)
		count = self.xpParam.getParam(ExperienceParameter.PINGCOUNT)
		for i in range(0, self.mpConfig.getClientInterfaceCount()):
			 cmd = self.pingCommand(self.mpConfig.getClientIP(i),
				 self.mpConfig.getServerIP(), n = count)
			 self.mpTopo.commandTo(self.mpConfig.client, cmd)

	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				  " >> " + ExperienceIperf.PING_OUTPUT
		print(s)
		return s

	def loadParam(self):
		"""
		todo : param LD_PRELOAD ??
		"""
		self.time = self.xpParam.getParam(ExperienceParameter.IPERFTIME)
		self.parallel = self.xpParam.getParam(ExperienceParameter.IPERFPARALLEL)

	def prepare(self):
		Experience.prepare(self)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " +
				ExperienceIperf.IPERF_LOG)
		self.mpTopo.commandTo(self.mpConfig.server, "rm " +
				ExperienceIperf.SERVER_LOG)

	def getClientCmd(self):
		s = ExperienceIperf.IPERF_BIN + " -c " + self.mpConfig.getServerIP() + \
			" -t " + self.time + " -P " + self.parallel + " &>" + ExperienceIperf.IPERF_LOG
		print(s)
		return s

	def getServerCmd(self):
		s = "sudo " + ExperienceIperf.IPERF_BIN + " -s &>" + \
			ExperienceIperf.SERVER_LOG + "&"
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
