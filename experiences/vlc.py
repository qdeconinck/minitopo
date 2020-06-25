from core.experience import Experience, ExperienceParameter
import os

class VLC(Experience):
    NAME = "vlc"

    SERVER_LOG = "vlc_server.log"
    CLIENT_LOG = "vlc_client.log"
    VLC_BIN = "/home/mininet/vlc/vlc"
    PING_OUTPUT = "ping.log"

    def __init__(self, experience_parameter, topo, topo_config):
        super(VLC, self).__init__(experience_parameter, topo, topo_config)
        self.loadParam()
        self.ping()
        super(VLC, self).classic_run()

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                VLC.PING_OUTPUT )
        count = self.experience_parameter.get(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.topo_config.getClientInterfaceCount()):
             cmd = self.pingCommand(self.topo_config.getClientIP(i),
                 self.topo_config.getServerIP(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + VLC.PING_OUTPUT
        print(s)
        return s

    def loadParam(self):
        self.file = self.experience_parameter.get(ExperienceParameter.VLCFILE)
        self.time = self.experience_parameter.get(ExperienceParameter.VLCTIME)

    def prepare(self):
        super(VLC, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                VLC.CLIENT_LOG )
        self.topo.command_to(self.topo_config.client, "Xvfb :66 &")
        self.topo.command_to(self.topo_config.server, "rm " + \
                VLC.SERVER_LOG )
        if self.file  == "random":
            self.topo.command_to(self.topo_config.client,
                "dd if=/dev/urandom of=random bs=1K count=" + \
                self.random_size)

    def getVLCServerCmd(self):
        s = "/etc/init.d/apache2 restart &>" + VLC.SERVER_LOG + " "
        print(s)
        return s

    def getVLCClientCmd(self):
        s = "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/mininet/usr/lib/ && sudo ldconfig && " \
                + VLC.VLC_BIN + " -I dummy --x11-display :66" + \
                " --adaptive-logic 3 --no-loop --play-and-exit " + \
                " http://" + self.topo_config.getServerIP() + \
                "/" + self.file + " 2>&1 | grep -E '(Neb|halp|bandwidth|late|Buffering|buffering)' > " + VLC.CLIENT_LOG
        if self.time != "0" :
            s = s + " &"
        print(s)
        return s

    def clean(self):
        super(VLC, self).clean(self)
        if self.file  == "random":
            self.topo.command_to(self.topo_config.client, "rm random*")
        self.topo.command_to(self.topo_config.client, "pkill Xvfb")

    def run(self):
        cmd = self.getVLCServerCmd()
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 1")
        cmd = self.getVLCClientCmd()
        self.topo.command_to(self.topo_config.client, cmd)

        if self.time != "0" :
            self.topo.command_to(self.topo_config.client, "sleep " + self.time)
            self.topo.command_to(self.topo_config.client, "pkill -9 -f vlc")

        self.topo.command_to(self.topo_config.client, "sleep 2")
