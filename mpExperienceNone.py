from core.experience import Experience, ExperienceParameter

class  ExperienceNone(Experience):
	def __init__(self, xpParamFile, mpTopo, mpConfig):
		Experience.__init__(self, xpParamFile, mpTopo, mpConfig)
		Experience.classicRun(self)

	def prepare(self):
		Experience.prepare(self)

	def clean(self):
		Experience.clean(self)

	def run(self):
		self.mpTopo.getCLI()
