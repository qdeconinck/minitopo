from core.experiment import Experiment, ExperimentParameter
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
    IPERF_BIN = "iperf3"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(IPerf, self).__init__(experiment_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                IPerf.PING_OUTPUT)
        count = self.experiment_parameter.get(ExperimentParameter.PING_COUNT)
        for i in range(0, self.topo_config.client_interface_count()):
             cmd = self.ping_command(self.topo_config.get_client_ip(i),
                 self.topo_config.get_server_ip(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def ping_command(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + IPerf.PING_OUTPUT
        print(s)
        return s

    def load_parameters(self):
        self.time = self.experiment_parameter.get(IPerfParameter.TIME)
        self.parallel = self.experiment_parameter.get(IPerfParameter.PARALLEL)

    def prepare(self):
        super(IPerf, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " +
                IPerf.IPERF_LOG)
        self.topo.command_to(self.topo_config.server, "rm " +
                IPerf.SERVER_LOG)

    def getClientCmd(self):
        s = IPerf.IPERF_BIN + " -c " + self.topo_config.get_server_ip() + \
            " -t " + self.time + " -P " + self.parallel + " &>" + IPerf.IPERF_LOG
        print(s)
        return s

    def getServerCmd(self):
        s = "sudo " + IPerf.IPERF_BIN + " -s &>" + \
            IPerf.SERVER_LOG + "&"
        print(s)
        return s

    def clean(self):
        super(IPerf, self).clean()

    def run(self):
        cmd = self.getServerCmd()
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        cmd = self.getClientCmd()
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.client, "sleep 2")
