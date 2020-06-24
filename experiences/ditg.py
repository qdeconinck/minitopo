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


    def __init__(self, xpParamFile, mpTopo, mpConfig):
        super(DITG, self).__init__(xpParamFile, mpTopo, mpConfig)
        self.loadParam()
        self.ping()
        super(DITG, self).classicRun()

    def ping(self):
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                Experience.PING_OUTPUT)
        count = self.xpParam.getParam(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.mpConfig.getClientInterfaceCount()):
             cmd = self.pingCommand(self.mpConfig.getClientIP(i),
                 self.mpConfig.getServerIP(), n = count)
             self.mpTopo.commandTo(self.mpConfig.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + DITG.PING_OUTPUT
        print(s)
        return s

    def loadParam(self):
        self.kbytes = self.xpParam.getParam(ExperienceParameter.DITGKBYTES)
        self.constant_packet_size = self.xpParam.getParam(ExperienceParameter.DITGCONSTANTPACKETSIZE)
        self.mean_poisson_packets_sec = self.xpParam.getParam(ExperienceParameter.DITGMEANPOISSONPACKETSSEC)
        self.constant_packets_sec = self.xpParam.getParam(ExperienceParameter.DITGCONSTANTPACKETSSEC)
        self.bursts_on_packets_sec = self.xpParam.getParam(ExperienceParameter.DITGBURSTSONPACKETSSEC)
        self.bursts_off_packets_sec = self.xpParam.getParam(ExperienceParameter.DITGBURSTSOFFPACKETSSEC)

    def prepare(self):
        super(DITG, self).prepare()
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + DITG.DITG_LOG)
        self.mpTopo.commandTo(self.mpConfig.server, "rm " + DITG.DITG_SERVER_LOG)
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + DITG.DITG_TEMP_LOG)

    def getClientCmd(self):
        s = DITG.ITGSEND_BIN + " -a " + self.mpConfig.getServerIP() + \
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
        self.mpTopo.commandTo(self.mpConfig.server, cmd)

        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
        cmd = self.getClientCmd()
        self.mpTopo.commandTo(self.mpConfig.client, cmd)
        self.mpTopo.commandTo(self.mpConfig.server, "pkill -9 -f ITGRecv")
        self.mpTopo.commandTo(self.mpConfig.server, DITG.ITGDEC_BIN + " " + DITG.DITG_SERVER_TEMP_LOG + " &> " + DITG.DITG_SERVER_LOG)
        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
