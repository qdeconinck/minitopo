#!/usr/bin/python

from core.experiment import Experiment, ExperimentParameter, ExperimentParameter
from core.topo import Topo, TopoParameter

from mininet_builder import MininetBuilder

from experiments import EXPERIMENTS
from topos import TOPO_CONFIGS, TOPOS

import logging


class Runner(object):
    """
    Run an experiment described by `experiment_parameter_file` in the topology
    described by `topo_parameter_file` in the network environment built by
    `builder_type`.

    All the operations are done when calling the constructor.
    """
    def __init__(self, builder_type, topo_parameter_file, experiment_parameter_file):
        self.topo_parameter = TopoParameter(topo_parameter_file)
        self.set_builder(builder_type)
        self.set_topo()
        self.set_topo_config()
        self.start_topo()
        self.run_experiment(experiment_parameter_file)
        self.stop_topo()

    def set_builder(self, builder_type):
        """
        Currently the only builder type supported is Mininet...
        """
        if builder_type == Topo.MININET_BUILDER:
            self.topo_builder = MininetBuilder()
        else:
            raise Exception("I can not find the builder {}".format(builder_type))

    def set_topo(self):
        """
        Matches the name of the topo and find the corresponding Topo class.
        """
        t = self.topo_parameter.get(Topo.TOPO_ATTR)
        if t in TOPOS:
            self.topo = TOPOS[t](self.topo_builder, self.topo_parameter)
        else:
            raise Exception("Unknown topo: {}".format(t))

        logging.info("Using topo {}".format(self.topo))

    def set_topo_config(self):
        """
        Match the name of the topo and find the corresponding TopoConfig class.
        """
        t = self.topo_parameter.get(Topo.TOPO_ATTR)
        if t in TOPO_CONFIGS:
            self.topo_config = TOPO_CONFIGS[t](self.topo, self.topo_parameter)
        else:
            raise Exception("Unknown topo config: {}".format(t))

        logging.info("Using topo config {}".format(self.topo_config))

    def start_topo(self):
        """
        Initialize the topology with its configuration
        """
        self.topo.start_network()
        self.topo_config.configure_network()

    def run_experiment(self, experiment_parameter_file):
        """
        Match the name of the experiement and launch it
        """
        # Well, we need to load twice the experiment parameters, is it really annoying?
        xp = ExperimentParameter(experiment_parameter_file).get(ExperimentParameter.XP_TYPE)
        if xp in EXPERIMENTS:
            exp = EXPERIMENTS[xp](experiment_parameter_file, self.topo, self.topo_config)
            exp.classic_run()
        else:
            raise Exception("Unknown experiment {}".format(xp))

    def stop_topo(self):
        """
        Stop the topology
        """
        self.topo.stop_network()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Minitopo, a wrapper of Mininet to run multipath experiments")

    parser.add_argument("--topo_param_file", "-t", required=True,
        help="path to the topo parameter file")
    parser.add_argument("--experiment_param_file", "-x",
        help="path to the experiment parameter file")

    args = parser.parse_args()

    logging.basicConfig(format="%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s", level=logging.INFO)

    # XXX Currently, there is no alternate topo builder...
    Runner(Topo.MININET_BUILDER, args.topo_param_file, args.experiment_param_file)