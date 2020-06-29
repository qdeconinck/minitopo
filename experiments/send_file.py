from core.experiment import RandomFileExperiment, RandomFileParameter, ExperimentParameter
import os

class SendFile(RandomFileExperiment):
    NAME = "sendfile"

    SERVER_LOG = "sendfile_server.log"
    CLIENT_LOG = "sendfile_client.log"
    WGET_BIN = "./client"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        # Just rely on RandomFileExperiment
        super(SendFile, self).__init__(experiment_parameter_filename, topo, topo_config)

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                SendFile.PING_OUTPUT )
        count = self.experiment_parameter.get(ExperimentParameter.PING_COUNT)
        for i in range(0, self.topo_config.client_interface_count()):
             cmd = self.ping_command(self.topo_config.get_client_ip(i),
                 self.topo_config.get_server_ip(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def ping_command(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + SendFile.PING_OUTPUT
        print(s)
        return s

    def load_parameters(self):
        super(SendFile, self).load_parameters()

    def prepare(self):
        super(SendFile, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                SendFile.CLIENT_LOG )
        self.topo.command_to(self.topo_config.server, "rm " + \
                SendFile.SERVER_LOG )

    def getSendFileServerCmd(self):
        s = "./server &>" + SendFile.SERVER_LOG + "&"
        print(s)
        return s

    def getSendFileClientCmd(self):
        s = SendFile.WGET_BIN + " " + self.topo_config.get_server_ip() + " &>" + SendFile.CLIENT_LOG
        print(s)
        return s

    def clean(self):
        super(SendFile, self).clean()

    def run(self):
        cmd = self.getSendFileServerCmd()
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 0.1")
        cmd = self.getSendFileClientCmd()
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.client, "sleep 2")
