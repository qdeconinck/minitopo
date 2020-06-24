from core.experience import Experience, ExperienceParameter

class NoneExperience(Experience):
    NAME = "none"

    def __init__(self, xpParamFile, mpTopo, mpConfig):
        super(NoneExperience, self).__init__(xpParamFile, mpTopo, mpConfig)
        super(NoneExperience, self).classicRun()

    def prepare(self):
        Experience.prepare(self)

    def clean(self):
        Experience.clean(self)

    def run(self):
        self.mpTopo.getCLI()
