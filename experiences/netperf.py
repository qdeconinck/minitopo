from core.experience import Experience, ExperienceParameter
import os

class Netperf(Experience):
    NAME = "netperf"

    NETPERF_LOG = "netperf.log"
    NETSERVER_LOG = "netserver.log"
    NETPERF_BIN = "netperf"
    NETSERVER_BIN = "netserver"
    PING_OUTPUT = "ping.log"

    def __init__(self, experience_parameter_filename, topo, topo_config):
        super(Netperf, self).__init__(experience_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()
        super(Netperf, self).classic_run()

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                Netperf.PING_OUTPUT)
        count = self.experience_parameter.get(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.topo_config.getClientInterfaceCount()):
             cmd = self.pingCommand(self.topo_config.getClientIP(i),
                 self.topo_config.getServerIP(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + Netperf.PING_OUTPUT
        print(s)
        return s

    def load_parameters(self):
        self.testlen = self.experience_parameter.get(ExperienceParameter.NETPERFTESTLEN)
        self.testname = self.experience_parameter.get(ExperienceParameter.NETPERFTESTNAME)
        self.reqres_size = self.experience_parameter.get(ExperienceParameter.NETPERFREQRESSIZE)

    def prepare(self):
        super(Netperf, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " +
                Netperf.NETPERF_LOG)
        self.topo.command_to(self.topo_config.server, "rm " +
                Netperf.NETSERVER_LOG)

    def getClientCmd(self):
        s = Netperf.NETPERF_BIN + " -H " + self.topo_config.getServerIP() + \
            " -l " + self.testlen + " -t " + self.testname + " -- -r " + self.reqres_size + \
            " &>" + Netperf.NETPERF_LOG
        print(s)
        return s

    def getServerCmd(self):
        s = "sudo " + Netperf.NETSERVER_BIN + " &>" + \
            Netperf.NETSERVER_LOG + "&"
        print(s)
        return s

    def clean(self):
        super(Netperf, self).clean()

    def run(self):
        cmd = self.getServerCmd()
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        cmd = self.getClientCmd()
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.client, "sleep 2")
