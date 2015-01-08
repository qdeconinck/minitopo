from mpExperience import MpExperience
from mpParamXp import MpParamXp

class  MpExperiencePing(MpExperience): 

	PING_OUTPUT = "ping.log"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		MpExperience.__init__(self, xpParamFile, mpTopo, mpConfig)
		MpExperience.classicRun(self)	
	def prepapre(self):
		MpExperience.prepare(self)
	
	def clean(self):
		MpExperience.clean(self)

	def run(self):
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				MpExperiencePing.PING_OUTPUT )
		count = self.xpParam.getParam(MpParamXp.PINGCOUNT)
		for i in range(0, self.mpConfig.getClientInterfaceCount()):
			 cmd = self.pingCommand(self.mpConfig.getClientIP(i),
				 self.mpConfig.getServerIP(), n = count)
			 self.mpTopo.commandTo(self.mpConfig.client, cmd)

	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				  " >> " + MpExperiencePing.PING_OUTPUT
		print(s)
		return s
