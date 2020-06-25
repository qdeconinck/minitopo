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

    def __init__(self, experience_parameter, topo, topo_config):
        super(SiriHTTP, self).__init__(experience_parameter, topo, topo_config)
        self.loadParam()
        self.ping()
        super(SiriHTTP, self).classic_run()

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                SiriHTTP.PING_OUTPUT )
        count = self.experience_parameter.get(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.topo_config.getClientInterfaceCount()):
             cmd = self.pingCommand(self.topo_config.getClientIP(i),
                 self.topo_config.getServerIP(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + SiriHTTP.PING_OUTPUT
        print(s)
        return s

    def loadParam(self):
        self.run_time = self.experience_parameter.get(ExperienceParameter.SIRIRUNTIME)
        self.query_size = self.experience_parameter.get(ExperienceParameter.SIRIQUERYSIZE)
        self.response_size = self.experience_parameter.get(ExperienceParameter.SIRIRESPONSESIZE)
        self.delay_query_response = self.experience_parameter.get(ExperienceParameter.SIRIDELAYQUERYRESPONSE)
        self.min_payload_size = self.experience_parameter.get(ExperienceParameter.SIRIMINPAYLOADSIZE)
        self.max_payload_size = self.experience_parameter.get(ExperienceParameter.SIRIMAXPAYLOADSIZE)
        self.interval_time_ms = self.experience_parameter.get(ExperienceParameter.SIRIINTERVALTIMEMS)
        self.buffer_size = self.experience_parameter.get(ExperienceParameter.SIRIBUFFERSIZE)
        self.burst_size = self.experience_parameter.get(ExperienceParameter.SIRIBURSTSIZE)
        self.interval_burst_time_ms = self.experience_parameter.get(ExperienceParameter.SIRIINTERVALBURSTTIMEMS)
        self.file = self.experience_parameter.get(ExperienceParameter.HTTPFILE)
        self.random_size = self.experience_parameter.get(ExperienceParameter.HTTPRANDOMSIZE)

    def prepare(self):
        super(SiriHTTP, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                SiriHTTP.CLIENT_LOG)
        self.topo.command_to(self.topo_config.server, "rm " + \
                SiriHTTP.SERVER_LOG)
        self.topo.command_to(self.topo_config.client, "rm " + \
                SiriHTTP.HTTP_CLIENT_LOG)
        self.topo.command_to(self.topo_config.server, "rm " + \
                SiriHTTP.HTTP_SERVER_LOG)
        if self.file  == "random":
            self.topo.command_to(self.topo_config.client,
                "dd if=/dev/urandom of=random bs=1K count=" + \
                self.random_size)


    def getSiriServerCmd(self):
        s = "python3 " + os.path.dirname(os.path.abspath(__file__))  + \
                "/utils/siri_server.py &>" + SiriHTTP.SERVER_LOG + "&"
        print(s)
        return s

    def getSiriClientCmd(self):
        s = SiriHTTP.JAVA_BIN + " -jar " + os.path.dirname(os.path.abspath(__file__))  + "/utils/siriClient.jar " + \
                self.topo_config.getServerIP() + " 8080 " + self.run_time + " " + self.query_size + " " + self.response_size + \
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
        s = SiriHTTP.WGET_BIN + " http://" + self.topo_config.getServerIP() + \
                "/" + self.file + " --no-check-certificate"
        print(s)
        return s

    def clean(self):
        super(SiriHTTP, self).clean()
        if self.file  == "random":
            self.topo.command_to(self.topo_config.client, "rm random*")

    def run(self):
        cmd = self.getSiriServerCmd()
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_before")
        self.topo.command_to(self.topo_config.server, cmd)
        cmd = self.getHTTPServerCmd()
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_before")
        cmd = self.getHTTPClientCmd()
        self.topo.command_to(self.topo_config.client, "for i in {1..200}; do " + cmd + "; done &")
        cmd = self.getSiriClientCmd()
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_after")
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_after")
        self.topo.command_to(self.topo_config.server, "pkill -f siri_server.py")
        self.topo.command_to(self.topo_config.client, "sleep 2")
