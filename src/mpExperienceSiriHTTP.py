from mpExperience import MpExperience
from mpParamXp import MpParamXp
from mpPvAt import MpPvAt
import os

class  MpExperienceSiriHTTP(MpExperience):
	HTTP_SERVER_LOG = "http_server.log"
	HTTP_CLIENT_LOG = "http_client.log"
	WGET_BIN = "wget"
	SERVER_LOG = "siri_server.log"
	CLIENT_LOG = "siri_client.log"
	CLIENT_ERR = "siri_client.err"
	JAVA_BIN = "java"
	PING_OUTPUT = "ping.log"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		MpExperience.__init__(self, xpParamFile, mpTopo, mpConfig)
		self.loadParam()
		self.ping()
		MpExperience.classicRun(self)

	def ping(self):
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				MpExperienceSiriHTTP.PING_OUTPUT )
		count = self.xpParam.getParam(MpParamXp.PINGCOUNT)
		for i in range(0, self.mpConfig.getClientInterfaceCount()):
			 cmd = self.pingCommand(self.mpConfig.getClientIP(i),
				 self.mpConfig.getServerIP(), n = count)
			 self.mpTopo.commandTo(self.mpConfig.client, cmd)

	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				  " >> " + MpExperienceSiriHTTP.PING_OUTPUT
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
		self.file = self.xpParam.getParam(MpParamXp.HTTPFILE)
		self.random_size = self.xpParam.getParam(MpParamXp.HTTPRANDOMSIZE)

	def prepare(self):
		MpExperience.prepare(self)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				MpExperienceSiriHTTP.CLIENT_LOG)
		self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
				MpExperienceSiriHTTP.SERVER_LOG)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				MpExperienceSiriHTTP.HTTP_CLIENT_LOG)
		self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
				MpExperienceSiriHTTP.HTTP_SERVER_LOG)
		if self.file  == "random":
			self.mpTopo.commandTo(self.mpConfig.client,
				"dd if=/dev/urandom of=random bs=1K count=" + \
				self.random_size)


	def getSiriServerCmd(self):
		s = "python3 " + os.path.dirname(os.path.abspath(__file__))  + \
				"/siri_server.py &>" + MpExperienceSiriHTTP.SERVER_LOG + "&"
		print(s)
		return s

	def getSiriClientCmd(self):
		s = MpExperienceSiriHTTP.JAVA_BIN + " -jar " + os.path.dirname(os.path.abspath(__file__))  + "/siriClient.jar " + \
				self.mpConfig.getServerIP() + " 8080 " + self.run_time + " " + self.query_size + " " + self.response_size + \
				" " + self.delay_query_response + " " + self.min_payload_size + " " + \
				self.max_payload_size  + " " + self.interval_time_ms + " " + self.buffer_size + " " + self.burst_size + " " + self.interval_burst_time_ms + \
				" >" + MpExperienceSiriHTTP.CLIENT_LOG + " 2>" + MpExperienceSiriHTTP.CLIENT_ERR
		print(s)
		return s

	def getHTTPServerCmd(self):
		s = "/etc/init.d/apache2 restart &>" + MpExperienceSiriHTTP.SERVER_LOG + "&"
		print(s)
		return s

	def getHTTPClientCmd(self):
		s = MpExperienceSiriHTTP.WGET_BIN + " http://" + self.mpConfig.getServerIP() + \
				"/" + self.file + " --no-check-certificate"
		print(s)
		return s

	def clean(self):
		MpExperience.clean(self)
		if self.file  == "random":
			self.mpTopo.commandTo(self.mpConfig.client, "rm random*")


	def run(self):
		cmd = self.getSiriServerCmd()
		self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_before")
		self.mpTopo.commandTo(self.mpConfig.server, cmd)
		cmd = self.getHTTPServerCmd()
		self.mpTopo.commandTo(self.mpConfig.server, cmd)

		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
		self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_before")
		cmd = self.getHTTPClientCmd()
		self.mpTopo.commandTo(self.mpConfig.client, "for i in {1..200}; do " + cmd + "; done &")
		cmd = self.getSiriClientCmd()
		self.mpTopo.commandTo(self.mpConfig.client, cmd)
		self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_after")
		self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_after")
		self.mpTopo.commandTo(self.mpConfig.server, "pkill -f siri_server.py")
		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
