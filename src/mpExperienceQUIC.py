from mpExperience import MpExperience
from mpParamXp import MpParamXp
import os


class MpExperienceQUIC(MpExperience):
	GO_BIN = "/usr/local/go/bin/go"
	SERVER_LOG = "quic_server.log"
	CLIENT_LOG = "quic_client.log"
	CLIENT_GO_FILE = "~/go/src/github.com/lucas-clemente/quic-go/example/client_benchmarker/main.go"
	SERVER_GO_FILE = "~/go/src/github.com/lucas-clemente/quic-go/example/main.go"
	CERTPATH = "~/go/src/github.com/lucas-clemente/quic-go/example/"
	PING_OUTPUT = "ping.log"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		MpExperience.__init__(self, xpParamFile, mpTopo, mpConfig)
		self.loadParam()
		self.ping()
		MpExperience.classicRun(self)

	def ping(self):
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				MpExperienceQUIC.PING_OUTPUT )
		count = self.xpParam.getParam(MpParamXp.PINGCOUNT)
		for i in range(0, self.mpConfig.getClientInterfaceCount()):
			 cmd = self.pingCommand(self.mpConfig.getClientIP(i),
				 self.mpConfig.getServerIP(), n = count)
			 self.mpTopo.commandTo(self.mpConfig.client, cmd)

	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				  " >> " + MpExperienceQUIC.PING_OUTPUT
		print(s)
		return s

	def loadParam(self):
		"""
		todo : param LD_PRELOAD ??
		"""
		self.file = self.xpParam.getParam(MpParamXp.HTTPSFILE)
		self.random_size = self.xpParam.getParam(MpParamXp.HTTPSRANDOMSIZE)
		self.multipath = self.xpParam.getParam(MpParamXp.QUICMULTIPATH)

	def prepare(self):
		MpExperience.prepare(self)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				MpExperienceQUIC.CLIENT_LOG )
		self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
				MpExperienceQUIC.SERVER_LOG )
		if self.file  == "random":
			self.mpTopo.commandTo(self.mpConfig.client,
				"dd if=/dev/urandom of=random bs=1K count=" + \
				self.random_size)

	def getQUICServerCmd(self):
		s = "./server_main"
		s += " -www . -certpath " + MpExperienceQUIC.CERTPATH + " -bind 0.0.0.0:6121 &>"
		s += MpExperienceQUIC.SERVER_LOG + " &"
		print(s)
		return s

	def getQUICClientCmd(self):
		s = "./main"
		if int(self.multipath) > 0:
			s += " -m"
		s += " -c https://" + self.mpConfig.getServerIP() + ":6121/random &>" + MpExperienceQUIC.CLIENT_LOG
		print(s)
		return s

	def getQUICClientPreCmd(self):
		s = "./main"
		if int(self.multipath) > 0:
			s += " -m"
		s += " -c https://" + self.mpConfig.getServerIP() + ":6121/ugfiugizuegiugzeffg &> quic_client_pre.log"
		print(s)
		return s

	def compileGoFiles(self):
		cmd = MpExperienceQUIC.GO_BIN + " build " + MpExperienceQUIC.SERVER_GO_FILE
		self.mpTopo.commandTo(self.mpConfig.server, cmd)
		self.mpTopo.commandTo(self.mpConfig.server, "mv main server_main")
		cmd = MpExperienceQUIC.GO_BIN + " build " + MpExperienceQUIC.CLIENT_GO_FILE
		self.mpTopo.commandTo(self.mpConfig.server, cmd)

	def clean(self):
		MpExperience.clean(self)
		if self.file  == "random":
			self.mpTopo.commandTo(self.mpConfig.client, "rm random*")

	def run(self):
		self.compileGoFiles()
		cmd = self.getQUICServerCmd()
		self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_before")
		self.mpTopo.commandTo(self.mpConfig.server, cmd)

		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")

		self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_before")

		cmd = self.getQUICClientPreCmd()
		self.mpTopo.commandTo(self.mpConfig.client, cmd)

		cmd = self.getQUICClientCmd()
		self.mpTopo.commandTo(self.mpConfig.client, cmd)
		self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_after")
		self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_after")

		self.mpTopo.commandTo(self.mpConfig.server, "pkill -f " + MpExperienceQUIC.SERVER_GO_FILE)

		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
		# Need to delete the go-build directory in tmp; could lead to no more space left error
		self.mpTopo.commandTo(self.mpConfig.client, "rm -r /tmp/go-build*")
		# Remove cache data
		self.mpTopo.commandTo(self.mpConfig.client, "rm cache_*")
