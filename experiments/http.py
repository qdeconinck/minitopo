from core.experiment import ExperimentParameter, RandomFileExperiment, RandomFileParameter
import logging
import os

class HTTP(RandomFileExperiment):
    NAME = "http"

    SERVER_LOG = "http_server.log"
    CLIENT_LOG = "http_client.log"
    WGET_BIN = "wget"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        # Just rely on RandomFileExperiment
        super(HTTP, self).__init__(experiment_parameter_filename, topo, topo_config)

    def load_parameters(self):
        # Just rely on RandomFileExperiment
        super(HTTP, self).load_parameters()

    def prepare(self):
        super(HTTP, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                HTTP.CLIENT_LOG )
        self.topo.command_to(self.topo_config.server, "rm " + \
                HTTP.SERVER_LOG )

    def getHTTPServerCmd(self):
        s = "python {}/../utils/http_server.py &> {}&".format(
            os.path.dirname(os.path.abspath(__file__)), HTTP.SERVER_LOG)
        logging.info(s)
        return s

    def getHTTPClientCmd(self):
        s = "(time {} http://{}/{} --no-check-certificate) &> {}".format(HTTP.WGET_BIN,
            self.topo_config.get_server_ip(), self.file, HTTP.CLIENT_LOG)
        logging.info(s)
        return s

    def clean(self):
        super(HTTP, self).clean()

    def run(self):
        cmd = self.getHTTPServerCmd()
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_before")
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        cmd = self.getHTTPClientCmd()
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_before")
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_after")
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_after")
        self.topo.command_to(self.topo_config.client, "sleep 2")
