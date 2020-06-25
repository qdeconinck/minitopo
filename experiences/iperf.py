from core.experience import Experience, ExperienceParameter
import os

class IPerf(Experience):
    NAME = "iperf"

    IPERF_LOG = "iperf.log"
    SERVER_LOG = "server.log"
    IPERF_BIN = "iperf3"
    PING_OUTPUT = "ping.log"

    def __init__(self, experience_parameter, topo, topo_config):
        super(IPerf, self).__init__(experience_parameter, topo, topo_config)
        self.loadParam()
        self.ping()
        super(IPerf, self).classic_run()

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                IPerf.PING_OUTPUT)
        count = self.experience_parameter.get(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.topo_config.getClientInterfaceCount()):
             cmd = self.pingCommand(self.topo_config.getClientIP(i),
                 self.topo_config.getServerIP(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + IPerf.PING_OUTPUT
        print(s)
        return s

    def loadParam(self):
        self.time = self.experience_parameter.get(ExperienceParameter.IPERFTIME)
        self.parallel = self.experience_parameter.get(ExperienceParameter.IPERFPARALLEL)

    def prepare(self):
        super(IPerf, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " +
                IPerf.IPERF_LOG)
        self.topo.command_to(self.topo_config.server, "rm " +
                IPerf.SERVER_LOG)

    def getClientCmd(self):
        s = IPerf.IPERF_BIN + " -c " + self.topo_config.getServerIP() + \
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
