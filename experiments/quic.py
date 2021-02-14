from core.experiment import RandomFileExperiment, RandomFileParameter, ExperimentParameter
from topos.multi_interface_multi_client import MultiInterfaceMultiClientConfig
import os


class QUICParameter(RandomFileParameter):
    MULTIPATH = "quicMultipath"

    def __init__(self, experiment_parameter_filename):
        super(QUICParameter, self).__init__(experiment_parameter_filename)
        self.default_parameters.update({
            QUICParameter.MULTIPATH: "0",
        })


class QUIC(RandomFileExperiment):
    NAME = "quic"
    PARAMETER_CLASS = QUICParameter

    GO_BIN = "/usr/local/go/bin/go"
    WGET = "~/git/wget/src/wget"
    SERVER_LOG = "quic_server.log"
    CLIENT_LOG = "quic_client.log"
    CLIENT_GO_FILE = "~/go/src/github.com/lucas-clemente/quic-go/example/client_benchmarker_cached/main.go"
    SERVER_GO_FILE = "~/go/src/github.com/lucas-clemente/quic-go/example/main.go"
    CERTPATH = "~/go/src/github.com/lucas-clemente/quic-go/example/"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        # Just rely on RandomFileExperiment
        super(QUIC, self).__init__(experiment_parameter_filename, topo, topo_config)

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                QUIC.PING_OUTPUT )
        count = self.experiment_parameter.get(ExperimentParameter.PING_COUNT)
        for i in range(0, self.topo_config.client_interface_count()):
             cmd = self.ping_command(self.topo_config.get_client_ip(i),
                 self.topo_config.get_server_ip(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def ping_command(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + QUIC.PING_OUTPUT
        print(s)
        return s

    def load_parameters(self):
        super(QUIC, self).load_parameters()
        self.multipath = self.experiment_parameter.get(QUICParameter.MULTIPATH)

    def prepare(self):
        super(QUIC, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                QUIC.CLIENT_LOG )
        self.topo.command_to(self.topo_config.server, "rm " + \
                QUIC.SERVER_LOG )

    def getQUICServerCmd(self):
        s = QUIC.GO_BIN + " run " + QUIC.SERVER_GO_FILE
        s += " -www . -certpath " + QUIC.CERTPATH + " &>"
        s += QUIC.SERVER_LOG + " &"
        print(s)
        return s

    def getQUICClientCmd(self):
        s = QUIC.GO_BIN + " run " + QUIC.CLIENT_GO_FILE
        if int(self.multipath) > 0:
            s += " -m"
        s += " https://" + self.topo_config.get_server_ip() + ":6121/random &>" + QUIC.CLIENT_LOG
        print(s)
        return s

    def getCongServerCmd(self, congID):
        s = "python " + os.path.dirname(os.path.abspath(__file__))  + \
                "/../utils/https_server.py &> https_server" + str(congID) + ".log &"
        print(s)
        return s

    def getCongClientCmd(self, congID):
        s = "(time " + QUIC.WGET + " https://" + self.topo_config.getCongServerIP(congID) +\
                 "/" + self.file + " --no-check-certificate --disable-mptcp) &> https_client" + str(congID) + ".log &"
        print(s)
        return s

    def clean(self):
        super(QUIC, self).clean()

    def run(self):
        cmd = self.getQUICServerCmd()
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_before")
        self.topo.command_to(self.topo_config.server, cmd)

        if isinstance(self.topo_config, MultiInterfaceMultiClientConfig):
            i = 0
            for cs in self.topo_config.cong_servers:
                cmd = self.getCongServerCmd(i)
                self.topo.command_to(cs, cmd)
                i = i + 1

        self.topo.command_to(self.topo_config.client, "sleep 2")

        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_before")
        # First run congestion clients, then the main one
        if isinstance(self.topo_config, MultiInterfaceMultiClientConfig):
            i = 0
            for cc in self.topo_config.cong_clients:
                cmd = self.getCongClientCmd(i)
                self.topo.command_to(cc, cmd)
                i = i + 1

        cmd = self.getQUICClientCmd()
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_after")
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_after")
        # Wait for congestion traffic to end
        if isinstance(self.topo_config, MultiInterfaceMultiClientConfig):
            for cc in self.topo_config.cong_clients:
                self.topo.command_to(cc, "while pkill -f wget -0; do sleep 0.5; done")

        self.topo.command_to(self.topo_config.server, "pkill -f " + QUIC.SERVER_GO_FILE)
        if isinstance(self.topo_config, MultiInterfaceMultiClientConfig):
            for cs in self.topo_config.cong_servers:
                self.topo.command_to(cs, "pkill -f https_server.py")

        self.topo.command_to(self.topo_config.client, "sleep 2")
        # Need to delete the go-build directory in tmp; could lead to no more space left error
        self.topo.command_to(self.topo_config.client, "rm -r /tmp/go-build*")
        # Remove cache data
        self.topo.command_to(self.topo_config.client, "rm cache_*")
