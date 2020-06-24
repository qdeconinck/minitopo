from core.experience import Experience, ExperienceParameter
import os

class Netperf(Experience):
    NAME = "netperf"

    NETPERF_LOG = "netperf.log"
    NETSERVER_LOG = "netserver.log"
    NETPERF_BIN = "netperf"
    NETSERVER_BIN = "netserver"
    PING_OUTPUT = "ping.log"

    def __init__(self, xpParamFile, mpTopo, mpConfig):
        super(Netperf, self).__init__(xpParamFile, mpTopo, mpConfig)
        self.loadParam()
        self.ping()
        super(Netperf, self).classicRun()

    def ping(self):
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                Netperf.PING_OUTPUT)
        count = self.xpParam.getParam(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.mpConfig.getClientInterfaceCount()):
             cmd = self.pingCommand(self.mpConfig.getClientIP(i),
                 self.mpConfig.getServerIP(), n = count)
             self.mpTopo.commandTo(self.mpConfig.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + Netperf.PING_OUTPUT
        print(s)
        return s

    def loadParam(self):
        self.testlen = self.xpParam.getParam(ExperienceParameter.NETPERFTESTLEN)
        self.testname = self.xpParam.getParam(ExperienceParameter.NETPERFTESTNAME)
        self.reqres_size = self.xpParam.getParam(ExperienceParameter.NETPERFREQRESSIZE)

    def prepare(self):
        super(Netperf, self).prepare()
        self.mpTopo.commandTo(self.mpConfig.client, "rm " +
                Netperf.NETPERF_LOG)
        self.mpTopo.commandTo(self.mpConfig.server, "rm " +
                Netperf.NETSERVER_LOG)

    def getClientCmd(self):
        s = Netperf.NETPERF_BIN + " -H " + self.mpConfig.getServerIP() + \
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
        self.mpTopo.commandTo(self.mpConfig.server, cmd)

        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
        cmd = self.getClientCmd()
        self.mpTopo.commandTo(self.mpConfig.client, cmd)
        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
