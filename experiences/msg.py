from core.experience import Experience, ExperienceParameter
import os

class Msg(Experience):
    NAME = "msg"

    SERVER_LOG = "msg_server.log"
    CLIENT_LOG = "msg_client.log"
    CLIENT_ERR = "msg_client.err"
    PING_OUTPUT = "ping.log"

    def __init__(self, xpParamFile, mpTopo, mpConfig):
        super(Msg, self).__init__(xpParamFile, mpTopo, mpConfig)
        self.loadParam()
        self.ping()
        super(Msg, self).classicRun()

    def ping(self):
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                Msg.PING_OUTPUT )
        count = self.xpParam.getParam(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.mpConfig.getClientInterfaceCount()):
             cmd = self.pingCommand(self.mpConfig.getClientIP(i),
                 self.mpConfig.getServerIP(), n = count)
             self.mpTopo.commandTo(self.mpConfig.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + Msg.PING_OUTPUT
        print(s)
        return s

    def loadParam(self):
        self.client_sleep = self.xpParam.getParam(ExperienceParameter.MSGCLIENTSLEEP)
        self.server_sleep = self.xpParam.getParam(ExperienceParameter.MSGSERVERSLEEP)
        self.nb_requests = self.xpParam.getParam(ExperienceParameter.MSGNBREQUESTS)
        self.bytes = self.xpParam.getParam(ExperienceParameter.MSGBYTES)

    def prepare(self):
        super(Msg, self).prepare()
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                Msg.CLIENT_LOG)
        self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
                Msg.SERVER_LOG)

    def getMsgServerCmd(self):
        s = "python " + os.path.dirname(os.path.abspath(__file__))  + \
                "/utils/msg_server.py --sleep " + self.server_sleep + " --bytes " + self.bytes + " &>" + Msg.SERVER_LOG + "&"
        print(s)
        return s

    def getMsgClientCmd(self):
        s = "python " + os.path.dirname(os.path.abspath(__file__))  + \
                "/utils/msg_client.py --sleep " + self.client_sleep + " --nb " + self.nb_requests + \
                " --bytes " + self.bytes + " >" + Msg.CLIENT_LOG + " 2>" + Msg.CLIENT_ERR
        print(s)
        return s

    def clean(self):
        super(Msg, self).clean()

    def run(self):
        cmd = self.getMsgServerCmd()
        self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_before")
        self.mpTopo.commandTo(self.mpConfig.server, cmd)

        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
        cmd = self.getMsgClientCmd()
        self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_before")
        self.mpTopo.commandTo(self.mpConfig.client, cmd)
        self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_after")
        self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_after")
        self.mpTopo.commandTo(self.mpConfig.server, "pkill -f msg_server.py")
        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
