from mpExperience import MpExperience
from mpParamXp import MpParamXp
import os


class MpExperienceQUICSiri(MpExperience):
	GO_BIN = "/usr/local/go/bin/go"
	SERVER_LOG = "quic_server.log"
	CLIENT_LOG = "quic_client.log"
	CLIENT_GO_FILE = "~/go/src/github.com/lucas-clemente/quic-go/example/siri/client/siri.go"
	SERVER_GO_FILE = "~/go/src/github.com/lucas-clemente/quic-go/example/siri/siri.go"
	PING_OUTPUT = "ping.log"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		MpExperience.__init__(self, xpParamFile, mpTopo, mpConfig)
		self.loadParam()
		self.ping()
		MpExperience.classicRun(self)

	def ping(self):
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				MpExperienceQUICSiri.PING_OUTPUT )
		count = self.xpParam.getParam(MpParamXp.PINGCOUNT)
		for i in range(0, self.mpConfig.getClientInterfaceCount()):
			 cmd = self.pingCommand(self.mpConfig.getClientIP(i),
				 self.mpConfig.getServerIP(), n = count)
			 self.mpTopo.commandTo(self.mpConfig.client, cmd)

	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				  " >> " + MpExperienceQUICSiri.PING_OUTPUT
		print(s)
		return s

	def loadParam(self):
		"""
		todo : param LD_PRELOAD ??
		"""
		self.run_time = self.xpParam.getParam(MpParamXp.QUICSIRIRUNTIME)
		self.multipath = self.xpParam.getParam(MpParamXp.QUICMULTIPATH)

	def prepare(self):
		MpExperience.prepare(self)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				MpExperienceQUICSiri.CLIENT_LOG )
		self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
				MpExperienceQUICSiri.SERVER_LOG )

	def getQUICSiriServerCmd(self):
		s = MpExperienceQUICSiri.GO_BIN + " run " + MpExperienceQUICSiri.SERVER_GO_FILE
		s += " -addr 0.0.0.0:8080 &>" + MpExperienceQUICSiri.SERVER_LOG + " &"
		print(s)
		return s

	def getQUICSiriClientCmd(self):
		s = MpExperienceQUICSiri.GO_BIN + " run " + MpExperienceQUICSiri.CLIENT_GO_FILE
		s += " -addr " + self.mpConfig.getServerIP() + ":8080 -runTime " + self.run_time + "s"
		if int(self.multipath) > 0:
			s += " -m"
		s += " &>" + MpExperienceQUICSiri.CLIENT_LOG
		print(s)
		return s

	def clean(self):
		MpExperience.clean(self)


	def run(self):
		cmd = self.getQUICSiriServerCmd()
		self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_before")
		self.mpTopo.commandTo(self.mpConfig.server, cmd)

		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
		cmd = self.getQUICSiriClientCmd()
		self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_before")
		self.mpTopo.commandTo(self.mpConfig.client, cmd)
		self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_after")
		self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_after")
		self.mpTopo.commandTo(self.mpConfig.server, "pkill -f " + MpExperienceQUICSiri.SERVER_GO_FILE)
		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
		# Need to delete the go-build directory in tmp; could lead to no more space left error
		self.mpTopo.commandTo(self.mpConfig.client, "rm -r /tmp/go-build*")
