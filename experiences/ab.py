from core.experience import Experience, ExperienceParameter
import os

class AB(Experience):
    NAME = "ab"

    SERVER_LOG = "ab_server.log"
    CLIENT_LOG = "ab_client.log"
    AB_BIN = "ab"
    PING_OUTPUT = "ping.log"

    def __init__(self, xpParamFile, mpTopo, mpConfig):
        super(AB, self).__init__(xpParamFile, mpTopo, mpConfig)
        self.loadParam()
        self.ping()
        super(AB, self).classicRun()

    def ping(self):
        self.mpTopo.commandTo(self.mpConfig.client,
                        "rm " + AB.PING_OUTPUT)
        count = self.xpParam.getParam(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.mpConfig.getClientInterfaceCount()):
             cmd = self.pingCommand(self.mpConfig.getClientIP(i),
                 self.mpConfig.getServerIP(), n = count)
             self.mpTopo.commandTo(self.mpConfig.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + AB.PING_OUTPUT
        print(s)
        return s

    def loadParam(self):
        self.file = self.xpParam.getParam(ExperienceParameter.HTTPFILE)
        self.random_size = self.xpParam.getParam(ExperienceParameter.HTTPRANDOMSIZE)
        self.concurrent_requests = self.xpParam.getParam(ExperienceParameter.ABCONCURRENTREQUESTS)
        self.timelimit = self.xpParam.getParam(ExperienceParameter.ABTIMELIMIT)

    def prepare(self):
        Experience.prepare(self)
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                AB.CLIENT_LOG )
        self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
                AB.SERVER_LOG )
        if self.file  == "random":
            self.mpTopo.commandTo(self.mpConfig.client,
                "dd if=/dev/urandom of=random bs=1K count=" + \
                self.random_size)

    def getAbServerCmd(self):
        s = "python " + os.path.dirname(os.path.abspath(__file__))  + \
                "/utils/http_server.py &>" + AB.SERVER_LOG + "&"
        print(s)
        return s

    def getAbClientCmd(self):
        s = AB.AB_BIN + " -c " + self.concurrent_requests + " -t " + \
             self.timelimit + " http://" + self.mpConfig.getServerIP() + "/" + self.file + \
            " &>" + AB.CLIENT_LOG
        print(s)
        return s

    def clean(self):
        Experience.clean(self)
        if self.file  == "random":
            self.mpTopo.commandTo(self.mpConfig.client, "rm random*")
        #todo use cst
        #self.mpTopo.commandTo(self.mpConfig.server, "killall netcat")


    def run(self):
        cmd = self.getAbServerCmd()
        self.mpTopo.commandTo(self.mpConfig.server, cmd)

        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
        cmd = self.getAbClientCmd()
        self.mpTopo.commandTo(self.mpConfig.client, cmd)
        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
