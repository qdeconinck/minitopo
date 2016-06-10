from mpExperience import MpExperience
from mpParamXp import MpParamXp
from mpPvAt import MpPvAt
import os

class  MpExperienceEpload(MpExperience):
	SERVER_LOG = "http_server.log"
	EPLOAD_LOG = "epload.log"
	NODE_BIN = "/usr/local/nodejs/bin/node"
	EPLOAD_EMULATOR="/home/mininet/epload/epload/emulator/run.js"
	PING_OUTPUT = "ping.log"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		MpExperience.__init__(self, xpParamFile, mpTopo, mpConfig)
		self.loadParam()
		self.ping()
		MpExperience.classicRun(self)

	def ping(self):
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				MpExperienceEpload.PING_OUTPUT )
		count = self.xpParam.getParam(MpParamXp.PINGCOUNT)
		for i in range(0, self.mpConfig.getClientInterfaceCount()):
			 cmd = self.pingCommand(self.mpConfig.getClientIP(i),
				 self.mpConfig.getServerIP(), n = count)
			 self.mpTopo.commandTo(self.mpConfig.client, cmd)

	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				  " >> " + MpExperienceEpload.PING_OUTPUT
		print(s)
		return s

	def loadParam(self):
		self.epload_test_dir = self.xpParam.getParam(MpParamXp.EPLOADTESTDIR)

	def prepare(self):
		MpExperience.prepare(self)
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				MpExperienceEpload.EPLOAD_LOG )
		self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
				MpExperienceEpload.SERVER_LOG )

	def getHTTPServerCmd(self):
		s = "/etc/init.d/apache2 restart &>" + MpExperienceEpload.SERVER_LOG + " &"
		print(s)
		return s

	def getKillHTTPCmd(self):
		s = "ps aux | grep SimpleHTTP | head -1 | tr -s ' ' | cut -d ' ' -f 2 | xargs kill"
		print(s)
		return s

	def getEploadClientCmd(self):
		s = MpExperienceEpload.NODE_BIN + " " + MpExperienceEpload.EPLOAD_EMULATOR + \
				" http " + \
				self.epload_test_dir + " &>" + MpExperienceEpload.EPLOAD_LOG
		print(s)
		return s

	def getSubHostCmd(self):
		s = "for f in `ls " + self.epload_test_dir + "/*`; do " + \
			" sed -i 's/@host@/" + self.mpConfig.getServerIP() + "/' " + \
			"$f; done"
		print(s)
		return s

	def getSubBackHostCmd(self):
		s = "for f in `ls " + self.epload_test_dir + "/*`; do " + \
			" sed -i 's/" + self.mpConfig.getServerIP() + "/@host@/' " + \
			"$f; done"
		print(s)
		return s

	def clean(self):
		MpExperience.clean(self)

	def run(self):
		cmd = self.getHTTPServerCmd()
		self.mpTopo.commandTo(self.mpConfig.server, cmd)
		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")

		cmd = self.getSubHostCmd()
		self.mpTopo.commandTo(self.mpConfig.client, cmd)
		cmd = self.getEploadClientCmd()
		self.mpTopo.commandTo(self.mpConfig.client, cmd)
		cmd = self.getSubBackHostCmd()
		self.mpTopo.commandTo(self.mpConfig.client, cmd)

		self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
		cmd = self.getKillHTTPCmd()
		self.mpTopo.commandTo(self.mpConfig.server, cmd)
