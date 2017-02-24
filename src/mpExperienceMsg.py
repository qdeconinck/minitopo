from mpExperience import MpExperience
from mpParamXp import MpParamXp
import os

class  MpExperienceMsg(MpExperience):
	SERVER_LOG = "msg_server.log"
	CLIENT_LOG = "msg_client.log"
	CLIENT_ERR = "msg_client.err"
	PING_OUTPUT = "ping.log"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		MpExperience.__init__(self, xpParamFile, mpTopo, mpConfig)
		self.loadParam()
		self.ping()
		MpExperience.classicRun(self)

	def ping(self):
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				MpExperienceMsg.PING_OUTPUT )
		count = self.xpParam.getParam(MpParamXp.PINGCOUNT)
		for i in range(0, self.mpConfig.getClientInterfaceCount()):
			 cmd = self.pingCommand(self.mpConfig.getClientIP(i),
				 self.mpConfig.getServerIP(), n = count)
			 self.mpTopo.commandTo(self.mpConfig.client, cmd)

	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				  " >> " + MpExperienceMsg.PING_OUTPUT
		print(s)
		return s

	def loadParam(self):
		"""
		todo : param LD_PRELOAD ??
		"""
		self.client_sleep = self.xpParam.getParam(MpParamXp.MSGCLIENTSLEEP)
		self.server_sleep = self.xpParam.getParam(MpParamXp.MSGSERVERSLEEP)
		self.nb_requests = self.xpParam.getParam(MpParamXp.MSGNBREQUESTS)

	def prepare(self):
		MpExperience.prepare(self)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				MpExperienceMsg.CLIENT_LOG)
		self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
				MpExperienceMsg.SERVER_LOG)

	def getMsgServerCmd(self):
		s = "python3 " + os.path.dirname(os.path.abspath(__file__))  + \
				"/msg_server.py --sleep " + self.server_sleep + " &>" + MpExperienceMsg.SERVER_LOG + "&"
		print(s)
		return s

	def getMsgClientCmd(self):
		s = "python3 " + os.path.dirname(os.path.abspath(__file__))  + \
				"/msg_client.py --sleep " + self.client_sleep + " --nb " + self.nb_requests + \
				" >" + MpExperienceMsg.CLIENT_LOG + " 2>" + MpExperienceSiriMsg.CLIENT_ERR + "&"
		print(s)
		return s

	def clean(self):
		MpExperience.clean(self)


	def run(self):
		cmd = self.getMsgServerCmd()
		self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_before")
		self.mpTopo.commandTo(self.mpConfig.server, cmd)

		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
		cmd = self.getMsgClientCmd()
		self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_before")
		self.mpTopo.commandTo(self.mpConfig.client, cmd)
		self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_after")
		self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_after")
		self.mpTopo.commandTo(self.mpConfig.server, "pkill -f msg_server.py")
		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
