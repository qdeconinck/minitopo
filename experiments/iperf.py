from core.experiment import Experiment, ExperimentParameter
import logging
import os


class IPerfParameter(ExperimentParameter):
    TIME = "iperfTime"
    PARALLEL = "iperfParallel"

    def __init__(self, experiment_parameter_filename):
        super(IPerfParameter, self).__init__(experiment_parameter_filename)
        self.default_parameters.update({
            IPerfParameter.TIME: "10",
            IPerfParameter.PARALLEL: "1",
        })

class IPerf(Experiment):
    NAME = "iperf"
    PARAMETER_CLASS = IPerfParameter

    IPERF_LOG = "iperf.log"
    SERVER_LOG = "server.log"
    IPERF_BIN = "iperf"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(IPerf, self).__init__(experiment_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()

    def load_parameters(self):
        self.time = self.experiment_parameter.get(IPerfParameter.TIME)
        self.parallel = self.experiment_parameter.get(IPerfParameter.PARALLEL)

    def prepare(self):
        super(IPerf, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm {}".format(IPerf.IPERF_LOG))
        self.topo.command_to(self.topo_config.server, "rm {}".format(IPerf.SERVER_LOG))

    def get_client_cmd(self):
        s = "{} -c {} -t {} -P {} -i 1 &>{}".format(IPerf.IPERF_BIN, 
            self.topo_config.get_server_ip(), self.time, self.parallel, IPerf.IPERF_LOG)
        logging.info(s)
        return s

    def get_server_cmd(self):
        s = "{} -s &> {} &".format(IPerf.IPERF_BIN, IPerf.SERVER_LOG)
        logging.info(s)
        return s

    def clean(self):
        super(IPerf, self).clean()

    def run(self):
        cmd = self.get_server_cmd()
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        cmd = self.get_client_cmd()
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.client, "sleep 2")
