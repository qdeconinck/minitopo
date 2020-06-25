from core.experience import Experience, ExperienceParameter
import os

class Msg(Experience):
    NAME = "msg"

    SERVER_LOG = "msg_server.log"
    CLIENT_LOG = "msg_client.log"
    CLIENT_ERR = "msg_client.err"
    PING_OUTPUT = "ping.log"

    def __init__(self, experience_parameter_filename, topo, topo_config):
        super(Msg, self).__init__(experience_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()
        super(Msg, self).classic_run()

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                Msg.PING_OUTPUT )
        count = self.experience_parameter.get(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.topo_config.getClientInterfaceCount()):
             cmd = self.pingCommand(self.topo_config.getClientIP(i),
                 self.topo_config.getServerIP(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + Msg.PING_OUTPUT
        print(s)
        return s

    def load_parameters(self):
        self.client_sleep = self.experience_parameter.get(ExperienceParameter.MSGCLIENTSLEEP)
        self.server_sleep = self.experience_parameter.get(ExperienceParameter.MSGSERVERSLEEP)
        self.nb_requests = self.experience_parameter.get(ExperienceParameter.MSGNBREQUESTS)
        self.bytes = self.experience_parameter.get(ExperienceParameter.MSGBYTES)

    def prepare(self):
        super(Msg, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                Msg.CLIENT_LOG)
        self.topo.command_to(self.topo_config.server, "rm " + \
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
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_before")
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        cmd = self.getMsgClientCmd()
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_before")
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_after")
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_after")
        self.topo.command_to(self.topo_config.server, "pkill -f msg_server.py")
        self.topo.command_to(self.topo_config.client, "sleep 2")
