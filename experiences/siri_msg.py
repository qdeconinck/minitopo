from core.experience import Experience, ExperienceParameter
import os

class SiriMsg(Experience):
    NAME = "sirimsg"

    MSG_SERVER_LOG = "msg_server.log"
    MSG_CLIENT_LOG = "msg_client.log"
    MSG_CLIENT_ERR = "msg_client.err"
    SERVER_LOG = "siri_server.log"
    CLIENT_LOG = "siri_client.log"
    CLIENT_ERR = "siri_client.err"
    JAVA_BIN = "java"
    PING_OUTPUT = "ping.log"

    def __init__(self, xpParamFile, mpTopo, mpConfig):
        super(SiriMsg, self).__init__(xpParamFile, mpTopo, mpConfig)
        self.loadParam()
        self.ping()
        super(SiriMsg, self).classicRun()

    def ping(self):
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                SiriMsg.PING_OUTPUT )
        count = self.xpParam.getParam(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.mpConfig.getClientInterfaceCount()):
             cmd = self.pingCommand(self.mpConfig.getClientIP(i),
                 self.mpConfig.getServerIP(), n = count)
             self.mpTopo.commandTo(self.mpConfig.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + SiriMsg.PING_OUTPUT
        print(s)
        return s

    def loadParam(self):
        self.run_time = self.xpParam.getParam(ExperienceParameter.SIRIRUNTIME)
        self.query_size = self.xpParam.getParam(ExperienceParameter.SIRIQUERYSIZE)
        self.response_size = self.xpParam.getParam(ExperienceParameter.SIRIRESPONSESIZE)
        self.delay_query_response = self.xpParam.getParam(ExperienceParameter.SIRIDELAYQUERYRESPONSE)
        self.min_payload_size = self.xpParam.getParam(ExperienceParameter.SIRIMINPAYLOADSIZE)
        self.max_payload_size = self.xpParam.getParam(ExperienceParameter.SIRIMAXPAYLOADSIZE)
        self.interval_time_ms = self.xpParam.getParam(ExperienceParameter.SIRIINTERVALTIMEMS)
        self.buffer_size = self.xpParam.getParam(ExperienceParameter.SIRIBUFFERSIZE)
        self.burst_size = self.xpParam.getParam(ExperienceParameter.SIRIBURSTSIZE)
        self.interval_burst_time_ms = self.xpParam.getParam(ExperienceParameter.SIRIINTERVALBURSTTIMEMS)
        self.client_sleep = self.xpParam.getParam(ExperienceParameter.MSGCLIENTSLEEP)
        self.server_sleep = self.xpParam.getParam(ExperienceParameter.MSGSERVERSLEEP)
        self.nb_requests = self.xpParam.getParam(ExperienceParameter.MSGNBREQUESTS)

    def prepare(self):
        super(SiriMsg, self).prepare()
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                SiriMsg.CLIENT_LOG)
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                SiriMsg.CLIENT_ERR)
        self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
                SiriMsg.SERVER_LOG)
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                SiriMsg.MSG_CLIENT_LOG)
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                SiriMsg.MSG_CLIENT_ERR)
        self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
                SiriMsg.MSG_SERVER_LOG)

    def getSiriServerCmd(self):
        s = "python3 " + os.path.dirname(os.path.abspath(__file__))  + \
                "/utils/siri_server.py &>" + SiriMsg.SERVER_LOG + "&"
        print(s)
        return s

    def getSiriClientCmd(self):
        s = SiriMsg.JAVA_BIN + " -jar " + os.path.dirname(os.path.abspath(__file__))  + "/utils/siriClient.jar " + \
                self.mpConfig.getServerIP() + " 8080 " + self.run_time + " " + self.query_size + " " + self.response_size + \
                " " + self.delay_query_response + " " + self.min_payload_size + " " + \
                self.max_payload_size  + " " + self.interval_time_ms + " " + self.buffer_size + " " + self.burst_size + " " + self.interval_burst_time_ms + \
                " >" + SiriMsg.CLIENT_LOG + " 2>" + SiriMsg.CLIENT_ERR
        print(s)
        return s

    def getMsgServerCmd(self):
        s = "python3 " + os.path.dirname(os.path.abspath(__file__))  + \
                "/utils/msg_server.py --sleep " + self.server_sleep + " &>" + SiriMsg.MSG_SERVER_LOG + "&"
        print(s)
        return s

    def getMsgClientCmd(self):
        s = "python3 " + os.path.dirname(os.path.abspath(__file__))  + \
                "/utils/msg_client.py --sleep " + self.client_sleep + " --nb " + self.nb_requests + \
                " --bulk >" + SiriMsg.MSG_CLIENT_LOG + " 2>" + SiriMsg.MSG_CLIENT_ERR + "&"
        print(s)
        return s

    def clean(self):
        super(SiriMsg, self).clean()

    def run(self):
        cmd = self.getSiriServerCmd()
        self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_before")
        self.mpTopo.commandTo(self.mpConfig.server, cmd)
        cmd = self.getMsgServerCmd()
        self.mpTopo.commandTo(self.mpConfig.server, cmd)

        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
        self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_before")
        cmd = self.getMsgClientCmd()
        self.mpTopo.commandTo(self.mpConfig.client, cmd)
        cmd = self.getSiriClientCmd()
        self.mpTopo.commandTo(self.mpConfig.client, cmd)
        self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_after")
        self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_after")
        self.mpTopo.commandTo(self.mpConfig.server, "pkill -f siri_server.py")
        self.mpTopo.commandTo(self.mpConfig.server, "pkill -f msg_server.py")
        self.mpTopo.commandTo(self.mpConfig.server, "pkill -f msg_client.py")
        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
