from core.experiment import Experiment, ExperimentParameter
import os


class QUICSiriParameter(ExperimentParameter):
    MULTIPATH = "quicMultipath"
    RUN_TIME = "quicSiriRunTime"

    def __init__(self, experiment_parameter_filename):
        super(QUICSiriParameter, self).__init__(experiment_parameter_filename)
        self.default_parameters.update({
            QUICSiriParameter.MULTIPATH: "0",
        })


class QUICSiri(Experiment):
    NAME = "quicsiri"
    PARAMETER_CLASS = QUICSiriParameter

    GO_BIN = "/usr/local/go/bin/go"
    SERVER_LOG = "quic_server.log"
    CLIENT_LOG = "quic_client.log"
    CLIENT_GO_FILE = "~/go/src/github.com/lucas-clemente/quic-go/example/siri/client/siri.go"
    SERVER_GO_FILE = "~/go/src/github.com/lucas-clemente/quic-go/example/siri/siri.go"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(QUICSiri, self).__init__(experiment_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                QUICSiri.PING_OUTPUT )
        count = self.experiment_parameter.get(ExperimentParameter.PING_COUNT)
        for i in range(0, self.topo_config.client_interface_count()):
             cmd = self.ping_command(self.topo_config.get_client_ip(i),
                 self.topo_config.get_server_ip(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def ping_command(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + QUICSiri.PING_OUTPUT
        print(s)
        return s

    def load_parameters(self):
        self.run_time = self.experiment_parameter.get(QUICSiriParameter.RUN_TIME)
        self.multipath = self.experiment_parameter.get(QUICSiriParameter.MULTIPATH)

    def prepare(self):
        super(QUICSiri, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                QUICSiri.CLIENT_LOG )
        self.topo.command_to(self.topo_config.server, "rm " + \
                QUICSiri.SERVER_LOG )

    def get_quic_siri_server_cmd(self):
        s = "{} run {} -addr 0.0.0.0:8080 &> {} &".format(QUICSiri.GO_BIN,
            QUICSiri.SERVER_GO_FILE, QUICSiri.SERVER_LOG)
        print(s)
        return s

    def get_quic_siri_client_cmd(self):
        s = "{} run {} -addr {}:8080 -runTime {}s {} &> {}".format(QUICSiri.GO_BIN,
            QUICSiri.CLIENT_GO_FILE, self.topo_config.get_server_ip(), self.run_time,
            "-m" if int(self.multipath) > 0 else "", QUICSiri.CLIENT_LOG)
        print(s)
        return s

    def clean(self):
        super(QUICSiri, self).clean()

    def run(self):
        cmd = self.get_quic_siri_server_cmd()
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_before")
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        cmd = self.get_quic_siri_client_cmd()
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_before")
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_after")
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_after")
        self.topo.command_to(self.topo_config.server, "pkill -f " + QUICSiri.SERVER_GO_FILE)
        self.topo.command_to(self.topo_config.client, "sleep 2")
        # Need to delete the go-build directory in tmp; could lead to no more space left error
        self.topo.command_to(self.topo_config.client, "rm -r /tmp/go-build*")
