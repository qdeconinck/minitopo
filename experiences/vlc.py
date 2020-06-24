from core.experience import Experience, ExperienceParameter
import os

class VLC(Experience):
    NAME = "vlc"

    SERVER_LOG = "vlc_server.log"
    CLIENT_LOG = "vlc_client.log"
    VLC_BIN = "/home/mininet/vlc/vlc"
    PING_OUTPUT = "ping.log"

    def __init__(self, xpParamFile, mpTopo, mpConfig):
        super(VLC, self).__init__(xpParamFile, mpTopo, mpConfig)
        self.loadParam()
        self.ping()
        super(VLC, self).classicRun()

    def ping(self):
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                VLC.PING_OUTPUT )
        count = self.xpParam.getParam(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.mpConfig.getClientInterfaceCount()):
             cmd = self.pingCommand(self.mpConfig.getClientIP(i),
                 self.mpConfig.getServerIP(), n = count)
             self.mpTopo.commandTo(self.mpConfig.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + VLC.PING_OUTPUT
        print(s)
        return s

    def loadParam(self):
        self.file = self.xpParam.getParam(ExperienceParameter.VLCFILE)
        self.time = self.xpParam.getParam(ExperienceParameter.VLCTIME)

    def prepare(self):
        super(VLC, self).prepare()
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                VLC.CLIENT_LOG )
        self.mpTopo.commandTo(self.mpConfig.client, "Xvfb :66 &")
        self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
                VLC.SERVER_LOG )
        if self.file  == "random":
            self.mpTopo.commandTo(self.mpConfig.client,
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
                " http://" + self.mpConfig.getServerIP() + \
                "/" + self.file + " 2>&1 | grep -E '(Neb|halp|bandwidth|late|Buffering|buffering)' > " + VLC.CLIENT_LOG
        if self.time != "0" :
            s = s + " &"
        print(s)
        return s

    def clean(self):
        super(VLC, self).clean(self)
        if self.file  == "random":
            self.mpTopo.commandTo(self.mpConfig.client, "rm random*")
        self.mpTopo.commandTo(self.mpConfig.client, "pkill Xvfb")

    def run(self):
        cmd = self.getVLCServerCmd()
        self.mpTopo.commandTo(self.mpConfig.server, cmd)

        self.mpTopo.commandTo(self.mpConfig.client, "sleep 1")
        cmd = self.getVLCClientCmd()
        self.mpTopo.commandTo(self.mpConfig.client, cmd)

        if self.time != "0" :
            self.mpTopo.commandTo(self.mpConfig.client, "sleep " + self.time)
            self.mpTopo.commandTo(self.mpConfig.client, "pkill -9 -f vlc")

        self.mpTopo.commandTo(self.mpConfig.client, "sleep 2")
