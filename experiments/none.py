from core.experiment import Experiment, ExperimentParameter

class NoneExperiment(Experiment):
    NAME = "none"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(NoneExperiment, self).__init__(experiment_parameter_filename, topo, topo_config)

    def prepare(self):
        Experiment.prepare(self)

    def clean(self):
        Experiment.clean(self)

    def run(self):
        self.topo.get_cli()
