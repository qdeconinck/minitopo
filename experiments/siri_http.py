from core.experiment import ExperimentParameter, RandomFileExperiment, RandomFileParameter
from .siri import Siri
import os

class SiriHTTP(Siri, RandomFileExperiment):
    NAME = "sirihttp"

    HTTP_SERVER_LOG = "http_server.log"
    HTTP_CLIENT_LOG = "http_client.log"
    WGET_BIN = "wget"
    SERVER_LOG = "siri_server.log"
    CLIENT_LOG = "siri_client.log"
    CLIENT_ERR = "siri_client.err"
    JAVA_BIN = "java"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        # Just rely on RandomFileExperiment
        super(SiriHTTP, self).__init__(experiment_parameter_filename, topo, topo_config)

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                SiriHTTP.PING_OUTPUT )
        count = self.experiment_parameter.get(ExperimentParameter.PING_COUNT)
        for i in range(0, self.topo_config.client_interface_count()):
             cmd = self.ping_command(self.topo_config.get_client_ip(i),
                 self.topo_config.get_server_ip(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def ping_command(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + SiriHTTP.PING_OUTPUT
        print(s)
        return s

    def load_parameters(self):
        # Start collecting parameters of RandomFileExperiment and Siri
        super(SiriHTTP, self).load_parameters()

    def prepare(self):
        super(SiriHTTP, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                SiriHTTP.CLIENT_LOG)
        self.topo.command_to(self.topo_config.server, "rm " + \
                SiriHTTP.SERVER_LOG)
        self.topo.command_to(self.topo_config.client, "rm " + \
                SiriHTTP.HTTP_CLIENT_LOG)
        self.topo.command_to(self.topo_config.server, "rm " + \
                SiriHTTP.HTTP_SERVER_LOG)

    def get_http_server_cmd(self):
        s = "/etc/init.d/apache2 restart &>" + SiriHTTP.SERVER_LOG + "&"
        print(s)
        return s

    def get_http_client_cmd(self):
        s = SiriHTTP.WGET_BIN + " http://" + self.topo_config.get_server_ip() + \
                "/" + self.file + " --no-check-certificate"
        print(s)
        return s

    def clean(self):
        super(SiriHTTP, self).clean()

    def run(self):
        cmd = self.get_siri_server_cmd()
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_before")
        self.topo.command_to(self.topo_config.server, cmd)
        cmd = self.get_http_server_cmd()
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_before")
        cmd = self.get_http_client_cmd()
        self.topo.command_to(self.topo_config.client, "for i in {1..200}; do " + cmd + "; done &")
        cmd = self.get_siri_client_cmd()
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_after")
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_after")
        self.topo.command_to(self.topo_config.server, "pkill -f siri_server.py")
        self.topo.command_to(self.topo_config.client, "sleep 2")
