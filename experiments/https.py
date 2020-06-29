from core.experiment import ExperimentParameter, RandomFileExperiment, RandomFileParameter
import os

class HTTPS(RandomFileExperiment):
    NAME = "https"

    SERVER_LOG = "https_server.log"
    CLIENT_LOG = "https_client.log"
    WGET_BIN = "wget"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        # Just rely on RandomFileExperiment
        super(HTTPS, self).__init__(experiment_parameter_filename, topo, topo_config)

    def load_parameters(self):
        # Just rely on RandomFileExperiment
        super(HTTPS, self).load_parameters()

    def prepare(self):
        super(HTTPS, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                HTTPS.CLIENT_LOG )
        self.topo.command_to(self.topo_config.server, "rm " + \
                HTTPS.SERVER_LOG )

    def getHTTPSServerCmd(self):
        s = "python {}/../utils/https_server.py {}/../utils/server.pem &> {}&".format(os.path.dirname(os.path.abspath(__file__)),
            os.path.dirname(os.path.abspath(__file__)), HTTPS.SERVER_LOG)
        print(s)
        return s

    def getHTTPSClientCmd(self):
        s = "(time " + HTTPS.WGET_BIN + " https://" + self.topo_config.get_server_ip() + \
                "/" + self.file + " --no-check-certificate) &>" + HTTPS.CLIENT_LOG
        print(s)
        return s

    def clean(self):
        super(HTTPS, self).clean()

    def run(self):
        cmd = self.getHTTPSServerCmd()
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_before")
        self.topo.command_to(self.topo_config.server, cmd)

        print("Waiting for the server to run")
        self.topo.command_to(self.topo_config.client, "sleep 2")
        cmd = self.getHTTPSClientCmd()
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_before")
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_after")
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_after")
        self.topo.command_to(self.topo_config.server, "pkill -f https_server.py")
        self.topo.command_to(self.topo_config.client, "sleep 2")
