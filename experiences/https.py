from core.experience import Experience, ExperienceParameter
import os

class HTTPS(Experience):
    NAME = "https"

    SERVER_LOG = "https_server.log"
    CLIENT_LOG = "https_client.log"
    WGET_BIN = "wget"
    PING_OUTPUT = "ping.log"

    def __init__(self, xpParamFile, mpTopo, mpConfig):
        super(HTTPS, self).__init__(xpParamFile, mpTopo, mpConfig)
        self.loadParam()
        self.ping()
        super(HTTPS, self).classicRun()

    def ping(self):
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                HTTPS.PING_OUTPUT )
        count = self.xpParam.getParam(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.mpConfig.getClientInterfaceCount()):
             cmd = self.pingCommand(self.mpConfig.getClientIP(i),
                 self.mpConfig.getServerIP(), n = count)
             self.mpTopo.commandTo(self.mpConfig.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + HTTPS.PING_OUTPUT
        print(s)
        return s

    def loadParam(self):
        self.file = self.xpParam.getParam(ExperienceParameter.HTTPSFILE)
        self.random_size = self.xpParam.getParam(ExperienceParameter.HTTPSRANDOMSIZE)

    def prepare(self):
        super(HTTPS, self).prepare()
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                HTTPS.CLIENT_LOG )
        self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
                HTTPS.SERVER_LOG )
        if self.file  == "random":
            self.mpTopo.commandTo(self.mpConfig.client,
                "dd if=/dev/urandom of=random bs=1K count=" + \
                self.random_size)

    def getHTTPSServerCmd(self):
        s = "python {}/../utils/https_server.py {}/../utils/server.pem &> {}&".format(os.path.dirname(os.path.abspath(__file__)),
            os.path.dirname(os.path.abspath(__file__)), HTTPS.SERVER_LOG)
        print(s)
        return s

    def getHTTPSClientCmd(self):
        s = "(time " + HTTPS.WGET_BIN + " https://" + self.mpConfig.getServerIP() + \
                "/" + self.file + " --no-check-certificate) &>" + HTTPS.CLIENT_LOG
        print(s)
        return s

    def clean(self):
        super(HTTPS, self).clean()
        if self.file  == "random":
            self.mpTopo.commandTo(self.mpConfig.client, "rm random*")

    def run(self):
        cmd = self.getHTTPSServerCmd()
        self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_before")
        self.mpTopo.commandTo(self.mpConfig.server, cmd)

        print("Waiting for the server to run")
        self.mpTopo.commandTo(self.mpConfig.client, "sleep 15")
        cmd = self.getHTTPSClientCmd()
        self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_before")
        self.mpTopo.commandTo(self.mpConfig.client, cmd)
        self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_after")
        self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_after")
        self.mpTopo.commandTo(self.mpConfig.server, "pkill -f https_server.py")
        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
