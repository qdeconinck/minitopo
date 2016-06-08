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
	DITG_TEMP_LOG = "snd_log_file"
	DITG_SERVER_TEMP_LOG = "recv_log_file"
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
		self.kbytes = self.xpParam.getParam(MpParamXp.DITGKBYTES)
		self.mean_poisson_packets_sec = self.xpParam.getParam(MpParamXp.DITGMEANPOISSONPACKETSSEC)
		self.constant_packets_sec = self.xpParam.getParam(MpParamXp.DITGCONSTANTPACKETSSEC)
		self.bursts_on_packets_sec = self.xpParam.getParam(MpParamXp.DITGBURSTSONPACKETSSEC)
		self.bursts_off_packets_sec = self.xpParam.getParam(MpParamXp.DITGBURSTSOFFPACKETSSEC)

	def prepare(self):
		MpExperience.prepare(self)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + MpExperienceDITG.DITG_LOG)
		self.mpTopo.commandTo(self.mpConfig.server, "rm " + MpExperienceDITG.DITG_SERVER_LOG)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + MpExperienceDITG.DITG_TEMP_LOG)

	def getClientCmd(self):
		s = MpExperienceDITG.ITGSEND_BIN + " -a " + self.mpConfig.getServerIP() + \
			" -T TCP -k " + self.kbytes + " -l " + MpExperienceDITG.DITG_TEMP_LOG

		if self.mean_poisson_packets_sec != "0":
			s += " -O " + self.mean_poisson_packets_sec
		elif self.constant_packets_sec != "0":
			s += " -C " + self.constant_packets_sec
		elif self.bursts_on_packets_sec != "0" and self.bursts_off_packets_sec != "0":
			s += " -B C " + self.bursts_on_packets_sec + " C " + self.bursts_off_packets_sec

		s += " && " + MpExperienceDITG.ITGDEC_BIN + " " + MpExperienceDITG.DITG_TEMP_LOG + " &> " + MpExperienceDITG.DITG_LOG
		print(s)
		return s

	def getServerCmd(self):
		s = MpExperienceDITG.ITGRECV_BIN + " -l " + MpExperienceDITG.DITG_SERVER_TEMP_LOG + " &"
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
		self.mpTopo.commandTo(self.mpConfig.server, MpExperienceDITG.ITGDEC_BIN + " " + MpExperienceDITG.DITG_SERVER_TEMP_LOG + " &> " + MpExperienceDITG.DITG_SERVER_LOG)
		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
