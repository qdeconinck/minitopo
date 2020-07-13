from mpExperience import MpExperience
from mpParamXp import MpParamXp

class  MpExperienceNone(MpExperience):
	def __init__(self, xpParamFile, mpTopo, mpConfig):
		MpExperience.__init__(self, xpParamFile, mpTopo, mpConfig)
		MpExperience.classicRun(self)

	def prepare(self):
		MpExperience.prepare(self)

	def clean(self):
		MpExperience.clean(self)

	def run(self):
		self.mpTopo.getCLI()
