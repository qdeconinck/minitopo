from core.experience import Experience, ExperienceParameter
import os

class Epload(Experience):
    NAME = "epload"

    SERVER_LOG = "http_server.log"
    EPLOAD_LOG = "epload.log"
    NODE_BIN = "/usr/local/nodejs/bin/node"
    EPLOAD_EMULATOR="/home/mininet/epload/epload/emulator/run.js"
    PING_OUTPUT = "ping.log"

    def __init__(self, xpParamFile, mpTopo, mpConfig):
        super(Epload, self).__init__(xpParamFile, mpTopo, mpConfig)
        self.loadParam()
        self.ping()
        super(Epload, self).classicRun()

    def ping(self):
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                Epload.PING_OUTPUT )
        count = self.xpParam.getParam(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.mpConfig.getClientInterfaceCount()):
             cmd = self.pingCommand(self.mpConfig.getClientIP(i),
                 self.mpConfig.getServerIP(), n = count)
             self.mpTopo.commandTo(self.mpConfig.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + Epload.PING_OUTPUT
        print(s)
        return s

    def loadParam(self):
        self.epload_test_dir = self.xpParam.getParam(ExperienceParameter.EPLOADTESTDIR)

    def prepare(self):
        super(Epload, self).prepare()
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                Epload.EPLOAD_LOG )
        self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
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
                self.epload_test_dir + " &>" + Epload.EPLOAD_LOG
        print(s)
        return s

    def getSubHostCmd(self):
        s = "for f in `ls " + self.epload_test_dir + "/*`; do " + \
            " sed -i 's/@host@/" + self.mpConfig.getServerIP() + "/' " + \
            "$f; done"
        print(s)
        return s

    def getSubBackHostCmd(self):
        s = "for f in `ls " + self.epload_test_dir + "/*`; do " + \
            " sed -i 's/" + self.mpConfig.getServerIP() + "/@host@/' " + \
            "$f; done"
        print(s)
        return s

    def clean(self):
        super(Epload, self).clean()

    def run(self):
        cmd = self.getHTTPServerCmd()
        self.mpTopo.commandTo(self.mpConfig.server, cmd)
        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")

        cmd = self.getSubHostCmd()
        self.mpTopo.commandTo(self.mpConfig.client, cmd)
        cmd = self.getEploadClientCmd()
        self.mpTopo.commandTo(self.mpConfig.client, cmd)
        cmd = self.getSubBackHostCmd()
        self.mpTopo.commandTo(self.mpConfig.client, cmd)

        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
        cmd = self.getKillHTTPCmd()
        self.mpTopo.commandTo(self.mpConfig.server, cmd)
