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

    def __init__(self, experience_parameter_filename, topo, topo_config):
        super(SiriMsg, self).__init__(experience_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()
        super(SiriMsg, self).classic_run()

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                SiriMsg.PING_OUTPUT )
        count = self.experience_parameter.get(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.topo_config.getClientInterfaceCount()):
             cmd = self.pingCommand(self.topo_config.getClientIP(i),
                 self.topo_config.getServerIP(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + SiriMsg.PING_OUTPUT
        print(s)
        return s

    def load_parameters(self):
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
        self.client_sleep = self.experience_parameter.get(ExperienceParameter.MSGCLIENTSLEEP)
        self.server_sleep = self.experience_parameter.get(ExperienceParameter.MSGSERVERSLEEP)
        self.nb_requests = self.experience_parameter.get(ExperienceParameter.MSGNBREQUESTS)

    def prepare(self):
        super(SiriMsg, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                SiriMsg.CLIENT_LOG)
        self.topo.command_to(self.topo_config.client, "rm " + \
                SiriMsg.CLIENT_ERR)
        self.topo.command_to(self.topo_config.server, "rm " + \
                SiriMsg.SERVER_LOG)
        self.topo.command_to(self.topo_config.client, "rm " + \
                SiriMsg.MSG_CLIENT_LOG)
        self.topo.command_to(self.topo_config.client, "rm " + \
                SiriMsg.MSG_CLIENT_ERR)
        self.topo.command_to(self.topo_config.server, "rm " + \
                SiriMsg.MSG_SERVER_LOG)

    def getSiriServerCmd(self):
        s = "python3 " + os.path.dirname(os.path.abspath(__file__))  + \
                "/utils/siri_server.py &>" + SiriMsg.SERVER_LOG + "&"
        print(s)
        return s

    def getSiriClientCmd(self):
        s = SiriMsg.JAVA_BIN + " -jar " + os.path.dirname(os.path.abspath(__file__))  + "/utils/siriClient.jar " + \
                self.topo_config.getServerIP() + " 8080 " + self.run_time + " " + self.query_size + " " + self.response_size + \
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
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_before")
        self.topo.command_to(self.topo_config.server, cmd)
        cmd = self.getMsgServerCmd()
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_before")
        cmd = self.getMsgClientCmd()
        self.topo.command_to(self.topo_config.client, cmd)
        cmd = self.getSiriClientCmd()
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_after")
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_after")
        self.topo.command_to(self.topo_config.server, "pkill -f siri_server.py")
        self.topo.command_to(self.topo_config.server, "pkill -f msg_server.py")
        self.topo.command_to(self.topo_config.server, "pkill -f msg_client.py")
        self.topo.command_to(self.topo_config.client, "sleep 2")
