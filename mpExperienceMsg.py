from core.experience import Experience, ExperienceParameter
import os

class  ExperienceMsg(Experience):
	SERVER_LOG = "msg_server.log"
	CLIENT_LOG = "msg_client.log"
	CLIENT_ERR = "msg_client.err"
	PING_OUTPUT = "ping.log"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		Experience.__init__(self, xpParamFile, mpTopo, mpConfig)
		self.loadParam()
		self.ping()
		Experience.classicRun(self)

	def ping(self):
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				ExperienceMsg.PING_OUTPUT )
		count = self.xpParam.getParam(ExperienceParameter.PINGCOUNT)
		for i in range(0, self.mpConfig.getClientInterfaceCount()):
			 cmd = self.pingCommand(self.mpConfig.getClientIP(i),
				 self.mpConfig.getServerIP(), n = count)
			 self.mpTopo.commandTo(self.mpConfig.client, cmd)

	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				  " >> " + ExperienceMsg.PING_OUTPUT
		print(s)
		return s

	def loadParam(self):
		"""
		todo : param LD_PRELOAD ??
		"""
		self.client_sleep = self.xpParam.getParam(ExperienceParameter.MSGCLIENTSLEEP)
		self.server_sleep = self.xpParam.getParam(ExperienceParameter.MSGSERVERSLEEP)
		self.nb_requests = self.xpParam.getParam(ExperienceParameter.MSGNBREQUESTS)
		self.bytes = self.xpParam.getParam(ExperienceParameter.MSGBYTES)

	def prepare(self):
		Experience.prepare(self)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				ExperienceMsg.CLIENT_LOG)
		self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
				ExperienceMsg.SERVER_LOG)

	def getMsgServerCmd(self):
		s = "python " + os.path.dirname(os.path.abspath(__file__))  + \
				"/utils/msg_server.py --sleep " + self.server_sleep + " --bytes " + self.bytes + " &>" + ExperienceMsg.SERVER_LOG + "&"
		print(s)
		return s

	def getMsgClientCmd(self):
		s = "python " + os.path.dirname(os.path.abspath(__file__))  + \
				"/utils/msg_client.py --sleep " + self.client_sleep + " --nb " + self.nb_requests + \
				" --bytes " + self.bytes + " >" + ExperienceMsg.CLIENT_LOG + " 2>" + ExperienceMsg.CLIENT_ERR
		print(s)
		return s

	def clean(self):
		Experience.clean(self)


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
