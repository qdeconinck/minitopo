from core.experience import Experience, ExperienceParameter
import os

class SendFile(Experience):
    NAME = "sendfile"

    SERVER_LOG = "sendfile_server.log"
    CLIENT_LOG = "sendfile_client.log"
    WGET_BIN = "./client"
    PING_OUTPUT = "ping.log"

    def __init__(self, xpParamFile, mpTopo, mpConfig):
        super(SendFile, self).__init__(xpParamFile, mpTopo, mpConfig)
        self.loadParam()
        self.ping()
        super(SendFile, self).classicRun()

    def ping(self):
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                SendFile.PING_OUTPUT )
        count = self.xpParam.getParam(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.mpConfig.getClientInterfaceCount()):
             cmd = self.pingCommand(self.mpConfig.getClientIP(i),
                 self.mpConfig.getServerIP(), n = count)
             self.mpTopo.commandTo(self.mpConfig.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + SendFile.PING_OUTPUT
        print(s)
        return s

    def loadParam(self):
        self.file = self.xpParam.getParam(ExperienceParameter.HTTPSFILE)
        self.random_size = self.xpParam.getParam(ExperienceParameter.HTTPSRANDOMSIZE)

    def prepare(self):
        super(SendFile, self).prepare()
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                SendFile.CLIENT_LOG )
        self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
                SendFile.SERVER_LOG )
        if self.file  == "random":
            self.mpTopo.commandTo(self.mpConfig.client,
                "dd if=/dev/urandom of=random bs=1K count=" + \
                self.random_size)

    def getSendFileServerCmd(self):
        s = "./server &>" + SendFile.SERVER_LOG + "&"
        print(s)
        return s

    def getSendFileClientCmd(self):
        s = SendFile.WGET_BIN + " " + self.mpConfig.getServerIP() + " &>" + SendFile.CLIENT_LOG
        print(s)
        return s

    def clean(self):
        super(SendFile, self).clean()
        if self.file  == "random":
            self.mpTopo.commandTo(self.mpConfig.client, "rm random*")

    def run(self):
        cmd = self.getSendFileServerCmd()
        self.mpTopo.commandTo(self.mpConfig.server, cmd)

        self.mpTopo.commandTo(self.mpConfig.client, "sleep 0.1")
        cmd = self.getSendFileClientCmd()
        self.mpTopo.commandTo(self.mpConfig.client, cmd)
        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
