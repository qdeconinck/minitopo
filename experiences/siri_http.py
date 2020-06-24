from core.experience import Experience, ExperienceParameter
import os

class SiriHTTP(Experience):
    NAME = "sirihttp"

    HTTP_SERVER_LOG = "http_server.log"
    HTTP_CLIENT_LOG = "http_client.log"
    WGET_BIN = "wget"
    SERVER_LOG = "siri_server.log"
    CLIENT_LOG = "siri_client.log"
    CLIENT_ERR = "siri_client.err"
    JAVA_BIN = "java"
    PING_OUTPUT = "ping.log"

    def __init__(self, xpParamFile, mpTopo, mpConfig):
        super(SiriHTTP, self).__init__(xpParamFile, mpTopo, mpConfig)
        self.loadParam()
        self.ping()
        super(SiriHTTP, self).classicRun()

    def ping(self):
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                SiriHTTP.PING_OUTPUT )
        count = self.xpParam.getParam(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.mpConfig.getClientInterfaceCount()):
             cmd = self.pingCommand(self.mpConfig.getClientIP(i),
                 self.mpConfig.getServerIP(), n = count)
             self.mpTopo.commandTo(self.mpConfig.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + SiriHTTP.PING_OUTPUT
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
        self.file = self.xpParam.getParam(ExperienceParameter.HTTPFILE)
        self.random_size = self.xpParam.getParam(ExperienceParameter.HTTPRANDOMSIZE)

    def prepare(self):
        super(SiriHTTP, self).prepare()
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                SiriHTTP.CLIENT_LOG)
        self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
                SiriHTTP.SERVER_LOG)
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                SiriHTTP.HTTP_CLIENT_LOG)
        self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
                SiriHTTP.HTTP_SERVER_LOG)
        if self.file  == "random":
            self.mpTopo.commandTo(self.mpConfig.client,
                "dd if=/dev/urandom of=random bs=1K count=" + \
                self.random_size)


    def getSiriServerCmd(self):
        s = "python3 " + os.path.dirname(os.path.abspath(__file__))  + \
                "/utils/siri_server.py &>" + SiriHTTP.SERVER_LOG + "&"
        print(s)
        return s

    def getSiriClientCmd(self):
        s = SiriHTTP.JAVA_BIN + " -jar " + os.path.dirname(os.path.abspath(__file__))  + "/utils/siriClient.jar " + \
                self.mpConfig.getServerIP() + " 8080 " + self.run_time + " " + self.query_size + " " + self.response_size + \
                " " + self.delay_query_response + " " + self.min_payload_size + " " + \
                self.max_payload_size  + " " + self.interval_time_ms + " " + self.buffer_size + " " + self.burst_size + " " + self.interval_burst_time_ms + \
                " >" + SiriHTTP.CLIENT_LOG + " 2>" + SiriHTTP.CLIENT_ERR
        print(s)
        return s

    def getHTTPServerCmd(self):
        s = "/etc/init.d/apache2 restart &>" + SiriHTTP.SERVER_LOG + "&"
        print(s)
        return s

    def getHTTPClientCmd(self):
        s = SiriHTTP.WGET_BIN + " http://" + self.mpConfig.getServerIP() + \
                "/" + self.file + " --no-check-certificate"
        print(s)
        return s

    def clean(self):
        super(SiriHTTP, self).clean()
        if self.file  == "random":
            self.mpTopo.commandTo(self.mpConfig.client, "rm random*")

    def run(self):
        cmd = self.getSiriServerCmd()
        self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_before")
        self.mpTopo.commandTo(self.mpConfig.server, cmd)
        cmd = self.getHTTPServerCmd()
        self.mpTopo.commandTo(self.mpConfig.server, cmd)

        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
        self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_before")
        cmd = self.getHTTPClientCmd()
        self.mpTopo.commandTo(self.mpConfig.client, "for i in {1..200}; do " + cmd + "; done &")
        cmd = self.getSiriClientCmd()
        self.mpTopo.commandTo(self.mpConfig.client, cmd)
        self.mpTopo.commandTo(self.mpConfig.server, "netstat -sn > netstat_server_after")
        self.mpTopo.commandTo(self.mpConfig.client, "netstat -sn > netstat_client_after")
        self.mpTopo.commandTo(self.mpConfig.server, "pkill -f siri_server.py")
        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
