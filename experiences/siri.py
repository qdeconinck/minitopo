from core.experience import Experience, ExperienceParameter
import os

class Siri(Experience):
    NAME = "siri"

    SERVER_LOG = "siri_server.log"
    CLIENT_LOG = "siri_client.log"
    CLIENT_ERR = "siri_client.err"
    JAVA_BIN = "java"
    PING_OUTPUT = "ping.log"

    def __init__(self, experience_parameter, topo, topo_config):
        super(Siri, self).__init__(experience_parameter, topo, topo_config)
        self.loadParam()
        self.ping()
        super(Siri, self).classic_run()

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                Siri.PING_OUTPUT )
        count = self.experience_parameter.get(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.topo_config.getClientInterfaceCount()):
             cmd = self.pingCommand(self.topo_config.getClientIP(i),
                 self.topo_config.getServerIP(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + Siri.PING_OUTPUT
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

    def prepare(self):
        super(Siri, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                Siri.CLIENT_LOG)
        self.topo.command_to(self.topo_config.server, "rm " + \
                Siri.SERVER_LOG)

    def getSiriServerCmd(self):
        s = "python3 " + os.path.dirname(os.path.abspath(__file__))  + \
                "/utils/siri_server.py &>" + Siri.SERVER_LOG + "&"
        print(s)
        return s

    def getSiriClientCmd(self):
        s = Siri.JAVA_BIN + " -jar " + os.path.dirname(os.path.abspath(__file__))  + "/utils/siriClient.jar " + \
                self.topo_config.getServerIP() + " 8080 " + self.run_time + " " + self.query_size + " " + self.response_size + \
                " " + self.delay_query_response + " " + self.min_payload_size + " " + \
                self.max_payload_size  + " " + self.interval_time_ms + " " + self.buffer_size + " " + self.burst_size + " " + self.interval_burst_time_ms + \
                " >" + Siri.CLIENT_LOG + " 2>" + Siri.CLIENT_ERR
        print(s)
        return s

    def clean(self):
        super(Siri, self).clean()

    def run(self):
        cmd = self.getSiriServerCmd()
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_before")
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        cmd = self.getSiriClientCmd()
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_before")
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_after")
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_after")
        self.topo.command_to(self.topo_config.server, "pkill -f siri_server.py")
        self.topo.command_to(self.topo_config.client, "sleep 2")
