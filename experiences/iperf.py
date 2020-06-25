from core.experience import Experience, ExperienceParameter
import os

class IPerfParameter(ExperienceParameter):
    TIME = "iperfTime"
    PARALLEL = "iperfParallel"

    def __init__(self, experience_parameter_filename):
        super(IPerfParameter, self).__init__(experience_parameter_filename)
        self.default_parameters.update({
            IPerfParameter.TIME: "10",
            IPerfParameter.PARALLEL: "1",
        })

class IPerf(Experience):
    NAME = "iperf"
    PARAMETER_CLASS = IPerfParameter

    IPERF_LOG = "iperf.log"
    SERVER_LOG = "server.log"
    IPERF_BIN = "iperf3"
    PING_OUTPUT = "ping.log"

    def __init__(self, experience_parameter_filename, topo, topo_config):
        super(IPerf, self).__init__(experience_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                IPerf.PING_OUTPUT)
        count = self.experience_parameter.get(ExperienceParameter.PING_COUNT)
        for i in range(0, self.topo_config.getClientInterfaceCount()):
             cmd = self.pingCommand(self.topo_config.getClientIP(i),
                 self.topo_config.getServerIP(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + IPerf.PING_OUTPUT
        print(s)
        return s

    def load_parameters(self):
        self.time = self.experience_parameter.get(IPerfParameter.TIME)
        self.parallel = self.experience_parameter.get(IPerfParameter.PARALLEL)

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
