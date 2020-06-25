from core.experience import Experience, ExperienceParameter
import os

class AB(Experience):
    NAME = "ab"

    SERVER_LOG = "ab_server.log"
    CLIENT_LOG = "ab_client.log"
    AB_BIN = "ab"
    PING_OUTPUT = "ping.log"

    def __init__(self, experience_parameter, topo, topo_config):
        super(AB, self).__init__(experience_parameter, topo, topo_config)
        self.loadParam()
        self.ping()
        super(AB, self).classic_run()

    def ping(self):
        self.topo.command_to(self.topo_config.client,
                        "rm " + AB.PING_OUTPUT)
        count = self.experience_parameter.get(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.topo_config.getClientInterfaceCount()):
             cmd = self.pingCommand(self.topo_config.getClientIP(i),
                 self.topo_config.getServerIP(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + AB.PING_OUTPUT
        print(s)
        return s

    def loadParam(self):
        self.file = self.experience_parameter.get(ExperienceParameter.HTTPFILE)
        self.random_size = self.experience_parameter.get(ExperienceParameter.HTTPRANDOMSIZE)
        self.concurrent_requests = self.experience_parameter.get(ExperienceParameter.ABCONCURRENTREQUESTS)
        self.timelimit = self.experience_parameter.get(ExperienceParameter.ABTIMELIMIT)

    def prepare(self):
        Experience.prepare(self)
        self.topo.command_to(self.topo_config.client, "rm " + \
                AB.CLIENT_LOG )
        self.topo.command_to(self.topo_config.server, "rm " + \
                AB.SERVER_LOG )
        if self.file  == "random":
            self.topo.command_to(self.topo_config.client,
                "dd if=/dev/urandom of=random bs=1K count=" + \
                self.random_size)

    def getAbServerCmd(self):
        s = "python " + os.path.dirname(os.path.abspath(__file__))  + \
                "/utils/http_server.py &>" + AB.SERVER_LOG + "&"
        print(s)
        return s

    def getAbClientCmd(self):
        s = AB.AB_BIN + " -c " + self.concurrent_requests + " -t " + \
             self.timelimit + " http://" + self.topo_config.getServerIP() + "/" + self.file + \
            " &>" + AB.CLIENT_LOG
        print(s)
        return s

    def clean(self):
        Experience.clean(self)
        if self.file  == "random":
            self.topo.command_to(self.topo_config.client, "rm random*")
        #todo use cst
        #self.topo.command_to(self.topo_config.server, "killall netcat")


    def run(self):
        cmd = self.getAbServerCmd()
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        cmd = self.getAbClientCmd()
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.client, "sleep 2")
