from core.experience import Experience, ExperienceParameter
import os

class HTTP(Experience):
    NAME = "http"

    SERVER_LOG = "http_server.log"
    CLIENT_LOG = "http_client.log"
    WGET_BIN = "wget"
    PING_OUTPUT = "ping.log"

    def __init__(self, experience_parameter, topo, topo_config):
        super(HTTP, self).__init__(experience_parameter, topo, topo_config)
        self.loadParam()
        self.ping()
        super(HTTP, self).classic_run()

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                HTTP.PING_OUTPUT )
        count = self.experience_parameter.get(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.topo_config.getClientInterfaceCount()):
             cmd = self.pingCommand(self.topo_config.getClientIP(i),
                 self.topo_config.getServerIP(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + HTTP.PING_OUTPUT
        print(s)
        return s

    def loadParam(self):
        self.file = self.experience_parameter.get(ExperienceParameter.HTTPFILE)
        self.random_size = self.experience_parameter.get(ExperienceParameter.HTTPRANDOMSIZE)

    def prepare(self):
        super(HTTP, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                HTTP.CLIENT_LOG )
        self.topo.command_to(self.topo_config.server, "rm " + \
                HTTP.SERVER_LOG )
        if self.file  == "random":
            self.topo.command_to(self.topo_config.client,
                "dd if=/dev/urandom of=random bs=1K count=" + \
                self.random_size)

    def getHTTPServerCmd(self):
        s = "/etc/init.d/apache2 restart &>" + HTTP.SERVER_LOG + "&"
        print(s)
        return s

    def getHTTPClientCmd(self):
        s = "(time " + HTTP.WGET_BIN + " http://" + self.topo_config.getServerIP() + \
                "/" + self.file + " --no-check-certificate) &>" + HTTP.CLIENT_LOG
        print(s)
        return s

    def clean(self):
        super(HTTP, self).clean()
        if self.file  == "random":
            self.topo.command_to(self.topo_config.client, "rm random*")

    def run(self):
        cmd = self.getHTTPServerCmd()
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_before")
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        cmd = self.getHTTPClientCmd()
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_before")
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_after")
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_after")
        self.topo.command_to(self.topo_config.client, "sleep 2")
