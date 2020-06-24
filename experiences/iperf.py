from core.experience import Experience, ExperienceParameter
import os

class IPerf(Experience):
    NAME = "iperf"

    IPERF_LOG = "iperf.log"
    SERVER_LOG = "server.log"
    IPERF_BIN = "iperf3"
    PING_OUTPUT = "ping.log"

    def __init__(self, xpParamFile, mpTopo, mpConfig):
        super(IPerf, self).__init__(xpParamFile, mpTopo, mpConfig)
        self.loadParam()
        self.ping()
        super(IPerf, self).classicRun()

    def ping(self):
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                IPerf.PING_OUTPUT)
        count = self.xpParam.getParam(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.mpConfig.getClientInterfaceCount()):
             cmd = self.pingCommand(self.mpConfig.getClientIP(i),
                 self.mpConfig.getServerIP(), n = count)
             self.mpTopo.commandTo(self.mpConfig.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + IPerf.PING_OUTPUT
        print(s)
        return s

    def loadParam(self):
        self.time = self.xpParam.getParam(ExperienceParameter.IPERFTIME)
        self.parallel = self.xpParam.getParam(ExperienceParameter.IPERFPARALLEL)

    def prepare(self):
        super(IPerf, self).prepare()
        self.mpTopo.commandTo(self.mpConfig.client, "rm " +
                IPerf.IPERF_LOG)
        self.mpTopo.commandTo(self.mpConfig.server, "rm " +
                IPerf.SERVER_LOG)

    def getClientCmd(self):
        s = IPerf.IPERF_BIN + " -c " + self.mpConfig.getServerIP() + \
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
        self.mpTopo.commandTo(self.mpConfig.server, cmd)

        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
        cmd = self.getClientCmd()
        self.mpTopo.commandTo(self.mpConfig.client, cmd)
        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
