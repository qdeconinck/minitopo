from core.experience import Experience, ExperienceParameter

class  ExperiencePing(Experience):

	PING_OUTPUT = "ping.log"

	def __init__(self, xpParamFile, mpTopo, mpConfig):
		Experience.__init__(self, xpParamFile, mpTopo, mpConfig)
		Experience.classicRun(self)
	def prepapre(self):
		Experience.prepare(self)

	def clean(self):
		Experience.clean(self)

	def run(self):
		self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
				ExperiencePing.PING_OUTPUT )
		count = self.xpParam.getParam(ExperienceParameter.PINGCOUNT)
		for i in range(0, self.mpConfig.getClientInterfaceCount()):
			 cmd = self.pingCommand(self.mpConfig.getClientIP(i),
				 self.mpConfig.getServerIP(), n = count)
			 self.mpTopo.commandTo(self.mpConfig.client, cmd)

	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				  " >> " + ExperiencePing.PING_OUTPUT
		print(s)
		return s
