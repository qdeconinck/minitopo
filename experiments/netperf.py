from core.experiment import Experiment, ExperimentParameter
import os


class NetperfParameter(ExperimentParameter):
    TESTLEN = "netperfTestlen"
    TESTNAME = "netperfTestname"
    REQRES_SIZE = "netperfReqresSize"

    def __init__(self, experiment_parameter_filename):
        super(NetperfParameter, self).__init__(experiment_parameter_filename)
        self.default_parameters.update({
            NetperfParameter.TESTLEN: "10",
            NetperfParameter.TESTNAME: "TCP_RR",
            NetperfParameter.REQRES_SIZE: "2K,256",
        })


class Netperf(Experiment):
    NAME = "netperf"
    PARAMETER_CLASS = NetperfParameter

    NETPERF_LOG = "netperf.log"
    NETSERVER_LOG = "netserver.log"
    NETPERF_BIN = "netperf"
    NETSERVER_BIN = "netserver"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(Netperf, self).__init__(experiment_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                Netperf.PING_OUTPUT)
        count = self.experiment_parameter.get(ExperimentParameter.PING_COUNT)
        for i in range(0, self.topo_config.client_interface_count()):
             cmd = self.ping_command(self.topo_config.get_client_ip(i),
                 self.topo_config.get_server_ip(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def ping_command(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + Netperf.PING_OUTPUT
        print(s)
        return s

    def load_parameters(self):
        self.testlen = self.experiment_parameter.get(NetperfParameter.TESTLEN)
        self.testname = self.experiment_parameter.get(NetperfParameter.TESTNAME)
        self.reqres_size = self.experiment_parameter.get(NetperfParameter.REQRES_SIZE)

    def prepare(self):
        super(Netperf, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " +
                Netperf.NETPERF_LOG)
        self.topo.command_to(self.topo_config.server, "rm " +
                Netperf.NETSERVER_LOG)

    def get_client_cmd(self):
        s = "{} -H {} -l {} -t {} -- -r {} &> {}".format(Netperf.NETPERF_BIN,
            self.topo_config.get_server_ip(), self.testlen, self.testname, self.reqres_size,
            Netperf.NETPERF_LOG)
        print(s)
        return s

    def get_server_cmd(self):
        s = "sudo {} &> {} &".format(Netperf.NETSERVER_BIN, Netperf.NETSERVER_LOG)
        print(s)
        return s

    def clean(self):
        super(Netperf, self).clean()

    def run(self):
        cmd = self.get_server_cmd()
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        cmd = self.get_client_cmd()
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.client, "sleep 2")
