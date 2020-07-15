from core.experiment import Experiment, ExperimentParameter
from topos.multi_interface_multi_client import MultiInterfaceMultiClientTopo
import logging
import os


class IPerfScenarioParameter(ExperimentParameter):
    FM_SUBFLOWS = "iperfScenarioFMSublows"

    def __init__(self, experiment_parameter_filename):
        super(IPerfScenarioParameter, self).__init__(experiment_parameter_filename)
        self.default_parameters.update({
            IPerfScenarioParameter.FM_SUBFLOWS: "1",
        })


class IPerfScenario(Experiment):
    NAME = "iperfScenario"
    PARAMETER_CLASS = IPerfScenarioParameter

    IPERF_LOG = "iperf.log"
    SERVER_LOG = "server.log"
    IPERF_BIN = "iperf"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(IPerfScenario, self).__init__(experiment_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()

    def load_parameters(self):
        super(IPerfScenario, self).load_parameters()
        self.fm_subflows = self.experiment_parameter.get(IPerfScenarioParameter.FM_SUBFLOWS)

    def prepare(self):
        super(IPerfScenario, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm {}".format(IPerfScenario.IPERF_LOG))
        self.topo.command_to(self.topo_config.server, "rm {}".format(IPerfScenario.SERVER_LOG))

        if not isinstance(self.topo, MultiInterfaceMultiClientTopo):
            raise Exception("IPerfScenario only runs with MultiInterfaceMultiClientTopo")

    def get_client_iperf_cmd(self, server_ip, time, client_id):
        s = "{} -c {} -t {} -P 1 -i 5 &>{}{}".format(IPerfScenario.IPERF_BIN, server_ip, time, IPerfScenario.IPERF_LOG, client_id)
        logging.info(s)
        return s

    def get_server_cmd(self, server_id=0):
        s = "{} -s &> {}{} &".format(IPerfScenario.IPERF_BIN, IPerfScenario.SERVER_LOG, server_id)
        logging.info(s)
        return s

    def clean(self):
        super(IPerfScenario, self).clean()

    def run(self):

        self.topo.command_to(self.topo_config.router, "tcpdump -i any -w router.pcap &")
        # First run servers
        for l, s in enumerate(self.topo_config.servers):
            self.topo.command_to(s, self.get_server_cmd(server_id=l))

        # And set nb of subflows for fullmesh
        self.topo.command_to(self.topo_config.client, "echo {} > /sys/module/mptcp_fullmesh/parameters/num_subflows".format(self.fm_subflows))

        self.topo.command_to(self.topo_config.client, "sleep 2")

        # We run as follow.
        logging.info("This experiment last about 1 minute. Please wait...")
        cmd = "sleep 10 && {} &".format(self.get_client_iperf_cmd(self.topo_config.get_server_ip(interface_index=1), 20, 1))
        self.topo.command_to(self.topo_config.clients[1], cmd)
        cmd = "sleep 20 && {} &".format(self.get_client_iperf_cmd(self.topo_config.get_server_ip(interface_index=2), 20, 2))
        self.topo.command_to(self.topo_config.clients[2], cmd)
        cmd = "{} &".format(self.get_client_iperf_cmd(self.topo_config.get_server_ip(), 50, 0))
        self.topo.command_to(self.topo_config.client, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")

        # This is hacky
        self.topo.command_global("sysctl -w net.mptcp.mptcp_enabled=0")
        self.topo.command_global("sysctl -w net.ipv4.tcp_congestion_control=reno")
        
        self.topo.command_to(self.topo_config.client, "sleep 50")

        self.topo.command_to(self.topo_config.client, "echo 1 > /sys/module/mptcp_fullmesh/parameters/num_subflows")
