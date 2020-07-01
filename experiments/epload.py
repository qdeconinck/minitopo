from core.experiment import Experiment, ExperimentParameter
import os

class EploadParameter(ExperimentParameter):
    TEST_DIR = "test_dir"

    def __init__(self, experiment_parameter_filename):
        super(EploadParameter, self).__init__(experiment_parameter_filename)
        self.default_parameters.update({
            TEST_DIR: "/bla/bla/bla",
        })


class Epload(Experiment):
    NAME = "epload"
    PARAMETER_CLASS = EploadParameter

    SERVER_LOG = "http_server.log"
    EPLOAD_LOG = "epload.log"
    NODE_BIN = "/usr/local/nodejs/bin/node"
    EPLOAD_EMULATOR="/home/mininet/epload/epload/emulator/run.js"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(Epload, self).__init__(experiment_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()

    def load_parameters(self):
        self.test_dir = self.experiment_parameter.get(EploadParameter.TEST_DIR)

    def prepare(self):
        super(Epload, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                Epload.EPLOAD_LOG )
        self.topo.command_to(self.topo_config.server, "rm " + \
                Epload.SERVER_LOG )

    def get_http_server_cmd(self):
        s = "/etc/init.d/apache2 restart &>" + Epload.SERVER_LOG + " &"
        print(s)
        return s

    def getKillHTTPCmd(self):
        s = "ps aux | grep SimpleHTTP | head -1 | tr -s ' ' | cut -d ' ' -f 2 | xargs kill"
        print(s)
        return s

    def getEploadClientCmd(self):
        s = Epload.NODE_BIN + " " + Epload.EPLOAD_EMULATOR + \
                " http " + \
                self.test_dir + " &>" + Epload.EPLOAD_LOG
        print(s)
        return s

    def getSubHostCmd(self):
        s = "for f in `ls " + self.test_dir + "/*`; do " + \
            " sed -i 's/@host@/" + self.topo_config.get_server_ip() + "/' " + \
            "$f; done"
        print(s)
        return s

    def getSubBackHostCmd(self):
        s = "for f in `ls " + self.test_dir + "/*`; do " + \
            " sed -i 's/" + self.topo_config.get_server_ip() + "/@host@/' " + \
            "$f; done"
        print(s)
        return s

    def clean(self):
        super(Epload, self).clean()

    def run(self):
        cmd = self.get_http_server_cmd()
        self.topo.command_to(self.topo_config.server, cmd)
        self.topo.command_to(self.topo_config.client, "sleep 2")

        cmd = self.getSubHostCmd()
        self.topo.command_to(self.topo_config.client, cmd)
        cmd = self.getEploadClientCmd()
        self.topo.command_to(self.topo_config.client, cmd)
        cmd = self.getSubBackHostCmd()
        self.topo.command_to(self.topo_config.client, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        cmd = self.getKillHTTPCmd()
        self.topo.command_to(self.topo_config.server, cmd)
