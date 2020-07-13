from mpExperience import MpExperience
from mpMultiInterfaceCongConfig import MpMultiInterfaceCongConfig
from mpParamXp import MpParamXp
import os


class MpExperienceQUIC(MpExperience):
	GO_BIN = "/usr/local/go/bin/go"
	WGET = "~/git/wget/src/wget"
	SERVER_LOG = "quic_server.log"
	CLIENT_LOG = "quic_client.log"
	CLIENT_GO_FILE = "~/go/src/github.com/lucas-clemente/quic-go/example/client_benchmarker_cached/main.go"
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
		s = MpExperienceQUIC.GO_BIN + " run " + MpExperienceQUIC.SERVER_GO_FILE
		s += " -www . -certpath " + MpExperienceQUIC.CERTPATH + " &>"
		s += MpExperienceQUIC.SERVER_LOG + " &"
		print(s)
		return s

	def getQUICClientCmd(self):
		s = MpExperienceQUIC.GO_BIN + " run " + MpExperienceQUIC.CLIENT_GO_FILE
		if int(self.multipath) > 0:
			s += " -m"
		s += " https://" + self.mpConfig.getServerIP() + ":6121/random &>" + MpExperienceQUIC.CLIENT_LOG
		print(s)
		return s

	def getCongServerCmd(self, congID):
		s = "python " + os.path.dirname(os.path.abspath(__file__))  + \
				"/https.py &> https_server" + str(congID) + ".log &"
		print(s)
		return s

	def getCongClientCmd(self, congID):
		s = "(time " + MpExperienceQUIC.WGET + " https://" + self.mpConfig.getCongServerIP(congID) +\
		 		"/" + self.file + " --no-check-certificate --disable-mptcp) &> https_client" + str(congID) + ".log &"
		print(s)
		return s

	def clean(self):
		MpExperience.clean(self)
		if self.file  == "random":
			self.mpTopo.commandTo(self.mpConfig.client, "rm random*")
		#todo use cst
		#self.mpTopo.commandTo(self.mpConfig.server, "killall netcat")


	def run(self):
		cmd = self.getQUICServerCmd()
		self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_before")
		self.mpTopo.commandTo(self.mpConfig.server, cmd)

		if isinstance(self.mpConfig, MpMultiInterfaceCongConfig):
			i = 0
			for cs in self.mpConfig.cong_servers:
				cmd = self.getCongServerCmd(i)
				self.mpTopo.commandTo(cs, cmd)
				i = i + 1

		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")

		self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_before")
		# First run congestion clients, then the main one
		if isinstance(self.mpConfig, MpMultiInterfaceCongConfig):
			i = 0
			for cc in self.mpConfig.cong_clients:
				cmd = self.getCongClientCmd(i)
				self.mpTopo.commandTo(cc, cmd)
				i = i + 1

		cmd = self.getQUICClientCmd()
		self.mpTopo.commandTo(self.mpConfig.client, cmd)
		self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_after")
		self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_after")
		# Wait for congestion traffic to end
		if isinstance(self.mpConfig, MpMultiInterfaceCongConfig):
			for cc in self.mpConfig.cong_clients:
				self.mpTopo.commandTo(cc, "while pkill -f wget -0; do sleep 0.5; done")

		self.mpTopo.commandTo(self.mpConfig.server, "pkill -f " + MpExperienceQUIC.SERVER_GO_FILE)
		if isinstance(self.mpConfig, MpMultiInterfaceCongConfig):
			for cs in self.mpConfig.cong_servers:
				self.mpTopo.commandTo(cs, "pkill -f https.py")

		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
		# Need to delete the go-build directory in tmp; could lead to no more space left error
		self.mpTopo.commandTo(self.mpConfig.client, "rm -r /tmp/go-build*")
		# Remove cache data
		self.mpTopo.commandTo(self.mpConfig.client, "rm cache_*")
