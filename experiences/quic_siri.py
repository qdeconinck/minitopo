from core.experience import Experience, ExperienceParameter
import os


class QUICSiri(Experience):
    NAME = "quicsiri"

    GO_BIN = "/usr/local/go/bin/go"
    SERVER_LOG = "quic_server.log"
    CLIENT_LOG = "quic_client.log"
    CLIENT_GO_FILE = "~/go/src/github.com/lucas-clemente/quic-go/example/siri/client/siri.go"
    SERVER_GO_FILE = "~/go/src/github.com/lucas-clemente/quic-go/example/siri/siri.go"
    PING_OUTPUT = "ping.log"

    def __init__(self, experience_parameter_filename, topo, topo_config):
        super(QUICSiri, self).__init__(experience_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()
        super(QUICSiri, self).classic_run()

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                QUICSiri.PING_OUTPUT )
        count = self.experience_parameter.get(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.topo_config.getClientInterfaceCount()):
             cmd = self.pingCommand(self.topo_config.getClientIP(i),
                 self.topo_config.getServerIP(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + QUICSiri.PING_OUTPUT
        print(s)
        return s

    def load_parameters(self):
        self.run_time = self.experience_parameter.get(ExperienceParameter.QUICSIRIRUNTIME)
        self.multipath = self.experience_parameter.get(ExperienceParameter.QUICMULTIPATH)

    def prepare(self):
        super(QUICSiri, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                QUICSiri.CLIENT_LOG )
        self.topo.command_to(self.topo_config.server, "rm " + \
                QUICSiri.SERVER_LOG )

    def getQUICSiriServerCmd(self):
        s = QUICSiri.GO_BIN + " run " + QUICSiri.SERVER_GO_FILE
        s += " -addr 0.0.0.0:8080 &>" + QUICSiri.SERVER_LOG + " &"
        print(s)
        return s

    def getQUICSiriClientCmd(self):
        s = QUICSiri.GO_BIN + " run " + QUICSiri.CLIENT_GO_FILE
        s += " -addr " + self.topo_config.getServerIP() + ":8080 -runTime " + self.run_time + "s"
        if int(self.multipath) > 0:
            s += " -m"
        s += " &>" + QUICSiri.CLIENT_LOG
        print(s)
        return s

    def clean(self):
        super(QUICSiri, self).clean()

    def run(self):
        cmd = self.getQUICSiriServerCmd()
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_before")
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        cmd = self.getQUICSiriClientCmd()
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_before")
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_after")
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_after")
        self.topo.command_to(self.topo_config.server, "pkill -f " + QUICSiri.SERVER_GO_FILE)
        self.topo.command_to(self.topo_config.client, "sleep 2")
        # Need to delete the go-build directory in tmp; could lead to no more space left error
        self.topo.command_to(self.topo_config.client, "rm -r /tmp/go-build*")
