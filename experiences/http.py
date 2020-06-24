from core.experience import Experience, ExperienceParameter
import os

class HTTP(Experience):
    NAME = "http"

    SERVER_LOG = "http_server.log"
    CLIENT_LOG = "http_client.log"
    WGET_BIN = "wget"
    PING_OUTPUT = "ping.log"

    def __init__(self, xpParamFile, mpTopo, mpConfig):
        super(HTTP, self).__init__(xpParamFile, mpTopo, mpConfig)
        self.loadParam()
        self.ping()
        super(HTTP, self).classicRun()

    def ping(self):
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                HTTP.PING_OUTPUT )
        count = self.xpParam.getParam(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.mpConfig.getClientInterfaceCount()):
             cmd = self.pingCommand(self.mpConfig.getClientIP(i),
                 self.mpConfig.getServerIP(), n = count)
             self.mpTopo.commandTo(self.mpConfig.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + HTTP.PING_OUTPUT
        print(s)
        return s

    def loadParam(self):
        self.file = self.xpParam.getParam(ExperienceParameter.HTTPFILE)
        self.random_size = self.xpParam.getParam(ExperienceParameter.HTTPRANDOMSIZE)

    def prepare(self):
        super(HTTP, self).prepare()
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                HTTP.CLIENT_LOG )
        self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
                HTTP.SERVER_LOG )
        if self.file  == "random":
            self.mpTopo.commandTo(self.mpConfig.client,
                "dd if=/dev/urandom of=random bs=1K count=" + \
                self.random_size)

    def getHTTPServerCmd(self):
        s = "/etc/init.d/apache2 restart &>" + HTTP.SERVER_LOG + "&"
        print(s)
        return s

    def getHTTPClientCmd(self):
        s = "(time " + HTTP.WGET_BIN + " http://" + self.mpConfig.getServerIP() + \
                "/" + self.file + " --no-check-certificate) &>" + HTTP.CLIENT_LOG
        print(s)
        return s

    def clean(self):
        super(HTTP, self).clean()
        if self.file  == "random":
            self.mpTopo.commandTo(self.mpConfig.client, "rm random*")

    def run(self):
        cmd = self.getHTTPServerCmd()
        self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_before")
        self.mpTopo.commandTo(self.mpConfig.server, cmd)

        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
        cmd = self.getHTTPClientCmd()
        self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_before")
        self.mpTopo.commandTo(self.mpConfig.client, cmd)
        self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_after")
        self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_after")
        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
