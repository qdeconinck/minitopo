from core.experience import Experience, ExperienceParameter

class NoneExperience(Experience):
    NAME = "none"

    def __init__(self, experience_parameter_filename, topo, topo_config):
        super(NoneExperience, self).__init__(experience_parameter_filename, topo, topo_config)

    def prepare(self):
        Experience.prepare(self)

    def clean(self):
        Experience.clean(self)

    def run(self):
        self.topo.get_cli()
