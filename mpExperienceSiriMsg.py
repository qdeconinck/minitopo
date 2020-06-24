from core.experience import Experience, ExperienceParameter
from mpPvAt import MpPvAt
import os

class  ExperienceSiriMsg(Experience):
	MSG_SERVER_LOG = "msg_server.log"
	MSG_CLIENT_LOG = "msg_client.log"
	MSG_CLIENT_ERR = "msg_client.err"
	SERVER_LOG = "siri_server.log"
	CLIENT_LOG = "siri_client.log"
	CLIENT_ERR = "siri_client.err"
	JAVA_BIN = "java"
	PING_OUTPUT = "ping.log"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		Experience.__init__(self, xpParamFile, mpTopo, mpConfig)
		self.loadParam()
		self.ping()
		Experience.classicRun(self)

	def ping(self):
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				ExperienceSiriMsg.PING_OUTPUT )
		count = self.xpParam.getParam(MpParamXp.PINGCOUNT)
		for i in range(0, self.mpConfig.getClientInterfaceCount()):
			 cmd = self.pingCommand(self.mpConfig.getClientIP(i),
				 self.mpConfig.getServerIP(), n = count)
			 self.mpTopo.commandTo(self.mpConfig.client, cmd)

	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				  " >> " + ExperienceSiriMsg.PING_OUTPUT
		print(s)
		return s

	def loadParam(self):
		"""
		todo : param LD_PRELOAD ??
		"""
		self.run_time = self.xpParam.getParam(MpParamXp.SIRIRUNTIME)
		self.query_size = self.xpParam.getParam(MpParamXp.SIRIQUERYSIZE)
		self.response_size = self.xpParam.getParam(MpParamXp.SIRIRESPONSESIZE)
		self.delay_query_response = self.xpParam.getParam(MpParamXp.SIRIDELAYQUERYRESPONSE)
		self.min_payload_size = self.xpParam.getParam(MpParamXp.SIRIMINPAYLOADSIZE)
		self.max_payload_size = self.xpParam.getParam(MpParamXp.SIRIMAXPAYLOADSIZE)
		self.interval_time_ms = self.xpParam.getParam(MpParamXp.SIRIINTERVALTIMEMS)
		self.buffer_size = self.xpParam.getParam(MpParamXp.SIRIBUFFERSIZE)
		self.burst_size = self.xpParam.getParam(MpParamXp.SIRIBURSTSIZE)
		self.interval_burst_time_ms = self.xpParam.getParam(MpParamXp.SIRIINTERVALBURSTTIMEMS)
		self.client_sleep = self.xpParam.getParam(MpParamXp.MSGCLIENTSLEEP)
		self.server_sleep = self.xpParam.getParam(MpParamXp.MSGSERVERSLEEP)
		self.nb_requests = self.xpParam.getParam(MpParamXp.MSGNBREQUESTS)

	def prepare(self):
		Experience.prepare(self)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				ExperienceSiriMsg.CLIENT_LOG)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				ExperienceSiriMsg.CLIENT_ERR)
		self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
				ExperienceSiriMsg.SERVER_LOG)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				ExperienceSiriMsg.MSG_CLIENT_LOG)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				ExperienceSiriMsg.MSG_CLIENT_ERR)
		self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
				ExperienceSiriMsg.MSG_SERVER_LOG)

	def getSiriServerCmd(self):
		s = "python3 " + os.path.dirname(os.path.abspath(__file__))  + \
				"/siri_server.py &>" + ExperienceSiriMsg.SERVER_LOG + "&"
		print(s)
		return s

	def getSiriClientCmd(self):
		s = ExperienceSiriMsg.JAVA_BIN + " -jar " + os.path.dirname(os.path.abspath(__file__))  + "/siriClient.jar " + \
				self.mpConfig.getServerIP() + " 8080 " + self.run_time + " " + self.query_size + " " + self.response_size + \
				" " + self.delay_query_response + " " + self.min_payload_size + " " + \
				self.max_payload_size  + " " + self.interval_time_ms + " " + self.buffer_size + " " + self.burst_size + " " + self.interval_burst_time_ms + \
				" >" + ExperienceSiriMsg.CLIENT_LOG + " 2>" + ExperienceSiriMsg.CLIENT_ERR
		print(s)
		return s

	def getMsgServerCmd(self):
		s = "python3 " + os.path.dirname(os.path.abspath(__file__))  + \
				"/msg_server.py --sleep " + self.server_sleep + " &>" + ExperienceSiriMsg.MSG_SERVER_LOG + "&"
		print(s)
		return s

	def getMsgClientCmd(self):
		s = "python3 " + os.path.dirname(os.path.abspath(__file__))  + \
				"/msg_client.py --sleep " + self.client_sleep + " --nb " + self.nb_requests + \
				" --bulk >" + ExperienceSiriMsg.MSG_CLIENT_LOG + " 2>" + ExperienceSiriMsg.MSG_CLIENT_ERR + "&"
		print(s)
		return s

	def clean(self):
		Experience.clean(self)


	def run(self):
		cmd = self.getSiriServerCmd()
		self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_before")
		self.mpTopo.commandTo(self.mpConfig.server, cmd)
		cmd = self.getMsgServerCmd()
		self.mpTopo.commandTo(self.mpConfig.server, cmd)

		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
		self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_before")
		cmd = self.getMsgClientCmd()
		self.mpTopo.commandTo(self.mpConfig.client, cmd)
		cmd = self.getSiriClientCmd()
		self.mpTopo.commandTo(self.mpConfig.client, cmd)
		self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_after")
		self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_after")
		self.mpTopo.commandTo(self.mpConfig.server, "pkill -f siri_server.py")
		self.mpTopo.commandTo(self.mpConfig.server, "pkill -f msg_server.py")
		self.mpTopo.commandTo(self.mpConfig.server, "pkill -f msg_client.py")
		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
