from mpExperience import MpExperience
from mpParamXp import MpParamXp
from mpPvAt import MpPvAt
import os

class MpExperienceDITG(MpExperience):
	DITG_LOG = "ditg.log"
	DITG_SERVER_LOG = "ditg_server.log"
	ITGDEC_BIN = "/home/mininet/D-ITG-2.8.1-r1023/bin/ITGDec"
	ITGRECV_BIN = "/home/mininet/D-ITG-2.8.1-r1023/bin/ITGRecv"
	ITGSEND_BIN = "/home/mininet/D-ITG-2.8.1-r1023/bin/ITGSend"
	DITG_TEMP_LOG = "recv_log_file"
	PING_OUTPUT = "ping.log"


	def __init__(self, xpParamFile, mpTopo, mpConfig):
		MpExperience.__init__(self, xpParamFile, mpTopo, mpConfig)
		self.loadParam()
		self.ping()
		MpExperience.classicRun(self)

	def ping(self):
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				MpExperienceDITG.PING_OUTPUT)
		count = self.xpParam.getParam(MpParamXp.PINGCOUNT)
		for i in range(0, self.mpConfig.getClientInterfaceCount()):
			 cmd = self.pingCommand(self.mpConfig.getClientIP(i),
				 self.mpConfig.getServerIP(), n = count)
			 self.mpTopo.commandTo(self.mpConfig.client, cmd)

	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				  " >> " + MpExperienceDITG.PING_OUTPUT
		print(s)
		return s

	def loadParam(self):
		"""
		todo : param LD_PRELOAD ??
		"""
		self.bytes = self.xpParam.getParam(MpParamXp.DITGBYTES)
		self.mean_poisson_packets_sec = self.xpParam.getParam(MpParamXp.DITGMEANPOISSONPACKETSSEC)

	def prepare(self):
		MpExperience.prepare(self)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + MpExperienceDITG.IPERF_LOG)
		self.mpTopo.commandTo(self.mpConfig.server, "rm " + MpExperienceDITG.SERVER_LOG)

	def getClientCmd(self):
		s = MpExperienceDITG.ITGSEND_BIN + " -a " + self.mpConfig.getServerIP() + \
			" -T TCP -k " + self.bytes + " -O " + self.mean_poisson_packets_sec + " -l " + MpExperienceDITG.DITG_TEMP_LOG + " && " + \
			MpExperienceDITG.ITGDEC_BIN + " " + MpExperienceDITG.DITG_TEMP_LOG + " &> " + MpExperienceDITG.DITG_LOG
		print(s)
		return s

	def getServerCmd(self):
		s = MpExperienceDITG.ITGRECV_BIN + " &> " + MpExperienceDITG.DITG_SERVER_LOG + " &"
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
		self.mpTopo.commandTo(self.mpConfig.server, "pkill -9 -f ITGRecv")
		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
