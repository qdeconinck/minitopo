from core.experiment import Experiment, ExperimentParameter
import os


class DITGParameter(ExperimentParameter):
    KBYTES = "ditgKBytes"
    CONSTANT_PACKET_SIZE = "ditgConstantPacketSize"
    MEAN_POISSON_PACKETS_SEC = "ditgMeanPoissonPacketsSec"
    CONSTANT_PACKETS_SEC = "ditgConstantPacketsSec"
    BURSTS_ON_PACKETS_SEC = "ditgBurstsOnPacketsSec"
    BURSTS_OFF_PACKETS_SEC = "ditgBurstsOffPacketsSec"

    def __init__(self, experiment_parameter_filename):
        super(DITGParameter, self).__init__(experiment_parameter_filename)
        self.default_parameters.update({
            DITGParameter.KBYTES: "10000",
            DITGParameter.CONSTANT_PACKET_SIZE: "1428",
            DITGParameter.MEAN_POISSON_PACKETS_SEC: "0",
            DITGParameter.CONSTANT_PACKETS_SEC: "0",
            DITGParameter.BURSTS_ON_PACKETS_SEC: "0",
            DITGParameter.BURSTS_OFF_PACKETS_SEC: "0",
        })


class DITG(Experiment):
    NAME = "ditg"
    PARAMETER_CLASS = DITGParameter

    DITG_LOG = "ditg.log"
    DITG_SERVER_LOG = "ditg_server.log"
    ITGDEC_BIN = "/home/mininet/D-ITG-2.8.1-r1023/bin/ITGDec"
    ITGRECV_BIN = "/home/mininet/D-ITG-2.8.1-r1023/bin/ITGRecv"
    ITGSEND_BIN = "/home/mininet/D-ITG-2.8.1-r1023/bin/ITGSend"
    DITG_TEMP_LOG = "snd_log_file"
    DITG_SERVER_TEMP_LOG = "recv_log_file"
    PING_OUTPUT = "ping.log"


    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(DITG, self).__init__(experiment_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()

    def load_parameters(self):
        self.kbytes = self.experiment_parameter.get(DITGParameter.KBYTES)
        self.constant_packet_size = self.experiment_parameter.get(DITGParameter.CONSTANT_PACKET_SIZE)
        self.mean_poisson_packets_sec = self.experiment_parameter.get(DITGParameter.MEAN_POISSON_PACKETS_SEC)
        self.constant_packets_sec = self.experiment_parameter.get(DITGParameter.CONSTANT_PACKETS_SEC)
        self.bursts_on_packets_sec = self.experiment_parameter.get(DITGParameter.BURSTS_ON_PACKETS_SEC)
        self.bursts_off_packets_sec = self.experiment_parameter.get(DITGParameter.BURSTS_OFF_PACKETS_SEC)

    def prepare(self):
        super(DITG, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + DITG.DITG_LOG)
        self.topo.command_to(self.topo_config.server, "rm " + DITG.DITG_SERVER_LOG)
        self.topo.command_to(self.topo_config.client, "rm " + DITG.DITG_TEMP_LOG)

    def get_client_cmd(self):
        s = DITG.ITGSEND_BIN + " -a " + self.topo_config.get_server_ip() + \
            " -T TCP -k " + self.kbytes + " -l " + DITG.DITG_TEMP_LOG

        if self.constant_packet_size != "0":
            s += " -c " + self.constant_packet_size
        elif self.mean_poisson_packets_sec != "0":
            s += " -O " + self.mean_poisson_packets_sec
        elif self.constant_packets_sec != "0":
            s += " -C " + self.constant_packets_sec
        elif self.bursts_on_packets_sec != "0" and self.bursts_off_packets_sec != "0":
            s += " -B C " + self.bursts_on_packets_sec + " C " + self.bursts_off_packets_sec

        s += " && " + DITG.ITGDEC_BIN + " " + DITG.DITG_TEMP_LOG + " &> " + DITG.DITG_LOG
        print(s)
        return s

    def get_server_cmd(self):
        s = DITG.ITGRECV_BIN + " -l " + DITG.DITG_SERVER_TEMP_LOG + " &"
        print(s)
        return s

    def clean(self):
        super(DITG, self).clean()

    def run(self):
        cmd = self.get_server_cmd()
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        cmd = self.get_client_cmd()
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.server, "pkill -9 -f ITGRecv")
        self.topo.command_to(self.topo_config.server, DITG.ITGDEC_BIN + " " + DITG.DITG_SERVER_TEMP_LOG + " &> " + DITG.DITG_SERVER_LOG)
        self.topo.command_to(self.topo_config.client, "sleep 2")
