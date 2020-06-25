from core.experience import Experience, ExperienceParameter
import os

class SendFile(Experience):
    NAME = "sendfile"

    SERVER_LOG = "sendfile_server.log"
    CLIENT_LOG = "sendfile_client.log"
    WGET_BIN = "./client"
    PING_OUTPUT = "ping.log"

    def __init__(self, experience_parameter, topo, topo_config):
        super(SendFile, self).__init__(experience_parameter, topo, topo_config)
        self.loadParam()
        self.ping()
        super(SendFile, self).classic_run()

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                SendFile.PING_OUTPUT )
        count = self.experience_parameter.get(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.topo_config.getClientInterfaceCount()):
             cmd = self.pingCommand(self.topo_config.getClientIP(i),
                 self.topo_config.getServerIP(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + SendFile.PING_OUTPUT
        print(s)
        return s

    def loadParam(self):
        self.file = self.experience_parameter.get(ExperienceParameter.HTTPSFILE)
        self.random_size = self.experience_parameter.get(ExperienceParameter.HTTPSRANDOMSIZE)

    def prepare(self):
        super(SendFile, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                SendFile.CLIENT_LOG )
        self.topo.command_to(self.topo_config.server, "rm " + \
                SendFile.SERVER_LOG )
        if self.file  == "random":
            self.topo.command_to(self.topo_config.client,
                "dd if=/dev/urandom of=random bs=1K count=" + \
                self.random_size)

    def getSendFileServerCmd(self):
        s = "./server &>" + SendFile.SERVER_LOG + "&"
        print(s)
        return s

    def getSendFileClientCmd(self):
        s = SendFile.WGET_BIN + " " + self.topo_config.getServerIP() + " &>" + SendFile.CLIENT_LOG
        print(s)
        return s

    def clean(self):
        super(SendFile, self).clean()
        if self.file  == "random":
            self.topo.command_to(self.topo_config.client, "rm random*")

    def run(self):
        cmd = self.getSendFileServerCmd()
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 0.1")
        cmd = self.getSendFileClientCmd()
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.client, "sleep 2")
