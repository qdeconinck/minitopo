from core.experience import Experience, ExperienceParameter
import os

class EploadParameter(ExperienceParameter):
    TEST_DIR = "test_dir"

    def __init__(self, experience_parameter_filename):
        super(EploadParameter, self).__init__(experience_parameter_filename)
        self.default_parameters.update({
            TEST_DIR: "/bla/bla/bla",
        })


class Epload(Experience):
    NAME = "epload"
    PARAMETER_CLASS = EploadParameter

    SERVER_LOG = "http_server.log"
    EPLOAD_LOG = "epload.log"
    NODE_BIN = "/usr/local/nodejs/bin/node"
    EPLOAD_EMULATOR="/home/mininet/epload/epload/emulator/run.js"
    PING_OUTPUT = "ping.log"

    def __init__(self, experience_parameter_filename, topo, topo_config):
        super(Epload, self).__init__(experience_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                Epload.PING_OUTPUT )
        count = self.experience_parameter.get(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.topo_config.getClientInterfaceCount()):
             cmd = self.pingCommand(self.topo_config.getClientIP(i),
                 self.topo_config.getServerIP(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + Epload.PING_OUTPUT
        print(s)
        return s

    def load_parameters(self):
        self.test_dir = self.experience_parameter.get(EploadParameter.TEST_DIR)

    def prepare(self):
        super(Epload, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                Epload.EPLOAD_LOG )
        self.topo.command_to(self.topo_config.server, "rm " + \
                Epload.SERVER_LOG )

    def getHTTPServerCmd(self):
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
            " sed -i 's/@host@/" + self.topo_config.getServerIP() + "/' " + \
            "$f; done"
        print(s)
        return s

    def getSubBackHostCmd(self):
        s = "for f in `ls " + self.test_dir + "/*`; do " + \
            " sed -i 's/" + self.topo_config.getServerIP() + "/@host@/' " + \
            "$f; done"
        print(s)
        return s

    def clean(self):
        super(Epload, self).clean()

    def run(self):
        cmd = self.getHTTPServerCmd()
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
