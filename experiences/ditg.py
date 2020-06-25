from core.experience import Experience, ExperienceParameter
import os

class DITG(Experience):
    NAME = "ditg"

    DITG_LOG = "ditg.log"
    DITG_SERVER_LOG = "ditg_server.log"
    ITGDEC_BIN = "/home/mininet/D-ITG-2.8.1-r1023/bin/ITGDec"
    ITGRECV_BIN = "/home/mininet/D-ITG-2.8.1-r1023/bin/ITGRecv"
    ITGSEND_BIN = "/home/mininet/D-ITG-2.8.1-r1023/bin/ITGSend"
    DITG_TEMP_LOG = "snd_log_file"
    DITG_SERVER_TEMP_LOG = "recv_log_file"
    PING_OUTPUT = "ping.log"


    def __init__(self, experience_parameter_filename, topo, topo_config):
        super(DITG, self).__init__(experience_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()
        super(DITG, self).classic_run()

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                Experience.PING_OUTPUT)
        count = self.experience_parameter.get(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.topo_config.getClientInterfaceCount()):
             cmd = self.pingCommand(self.topo_config.getClientIP(i),
                 self.topo_config.getServerIP(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + DITG.PING_OUTPUT
        print(s)
        return s

    def load_parameters(self):
        self.kbytes = self.experience_parameter.get(ExperienceParameter.DITGKBYTES)
        self.constant_packet_size = self.experience_parameter.get(ExperienceParameter.DITGCONSTANTPACKETSIZE)
        self.mean_poisson_packets_sec = self.experience_parameter.get(ExperienceParameter.DITGMEANPOISSONPACKETSSEC)
        self.constant_packets_sec = self.experience_parameter.get(ExperienceParameter.DITGCONSTANTPACKETSSEC)
        self.bursts_on_packets_sec = self.experience_parameter.get(ExperienceParameter.DITGBURSTSONPACKETSSEC)
        self.bursts_off_packets_sec = self.experience_parameter.get(ExperienceParameter.DITGBURSTSOFFPACKETSSEC)

    def prepare(self):
        super(DITG, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + DITG.DITG_LOG)
        self.topo.command_to(self.topo_config.server, "rm " + DITG.DITG_SERVER_LOG)
        self.topo.command_to(self.topo_config.client, "rm " + DITG.DITG_TEMP_LOG)

    def getClientCmd(self):
        s = DITG.ITGSEND_BIN + " -a " + self.topo_config.getServerIP() + \
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

    def getServerCmd(self):
        s = DITG.ITGRECV_BIN + " -l " + DITG.DITG_SERVER_TEMP_LOG + " &"
        print(s)
        return s

    def clean(self):
        super(DITG, self).clean()

    def run(self):
        cmd = self.getServerCmd()
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        cmd = self.getClientCmd()
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.server, "pkill -9 -f ITGRecv")
        self.topo.command_to(self.topo_config.server, DITG.ITGDEC_BIN + " " + DITG.DITG_SERVER_TEMP_LOG + " &> " + DITG.DITG_SERVER_LOG)
        self.topo.command_to(self.topo_config.client, "sleep 2")
