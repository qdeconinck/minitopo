from core.experience import Experience, ExperienceParameter

class Ping(Experience):
	NAME = "ping"

	PING_OUTPUT = "ping.log"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		super(Ping, self).__init__(xpParamFile, mpTopo, mpConfig)
		super(Ping, self).classicRun()

	def prepare(self):
		super(Ping, self).prepare()

	def clean(self):
		super(Ping, self).clean()

	def run(self):
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				Ping.PING_OUTPUT )
		count = self.xpParam.getParam(ExperienceParameter.PINGCOUNT)
		for i in range(0, self.mpConfig.getClientInterfaceCount()):
			 cmd = self.pingCommand(self.mpConfig.getClientIP(i),
				 self.mpConfig.getServerIP(), n = count)
			 self.mpTopo.commandTo(self.mpConfig.client, cmd)

	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				  " >> " + Ping.PING_OUTPUT
		print(s)
		return s
