from core.experience import Experience, ExperienceParameter

"""
Should be the mother of ExperienceNCPV, shame on me, should rewrite
ExperienceNCPV as daughter class of this one.
"""

class NC(Experience):
    NAME = "nc"

    SERVER_NC_LOG = "netcat_server"
    CLIENT_NC_LOG = "netcat_client"
    NC_BIN = "netcat"

    def __init__(self, xpParamFile, mpTopo, mpConfig):
        super(NC, self).__init__(xpParamFile, mpTopo, mpConfig)
        self.loadParam()
        super(NC, self).classicRun()
    
    def loadParam(self):
        self.ddibs = self.xpParam.getParam(ExperienceParameter.DDIBS)
        self.ddobs = self.xpParam.getParam(ExperienceParameter.DDOBS)
        self.ddcount = self.xpParam.getParam(ExperienceParameter.DDCOUNT)
        self.ncServerPort = self.xpParam.getParam(ExperienceParameter.NCSERVERPORT)
        self.ncClientPort = []
        for k in sorted(self.xpParam.paramDic):
            if k.startswith(ExperienceParameter.NCCLIENTPORT):
                port = self.xpParam.paramDic[k]
                self.ncClientPort.append(port)
        if len(self.ncClientPort) == 0:
            d = self.xpParam.getParam(ExperienceParameter.NCCLIENTPORT)
            self.ncClientPort.append(d)

    def prepare(self):
        super(NC, self).prepare()
        self.mpTopo.commandTo(self.mpConfig.client, "rm " + \
                NC.CLIENT_NC_LOG )
        self.mpTopo.commandTo(self.mpConfig.server, "rm " + \
                NC.SERVER_NC_LOG )

    def getNCServerCmd(self, id):
        s = "dd if=/dev/urandom ibs=" + self.ddibs + \
                " obs=" + self.ddobs + \
                " count=" + self.ddcount + \
                " | " + \
                NC.NC_BIN + \
                " -l " + self.ncServerPort  + \
                " &>" + NC.SERVER_NC_LOG + \
                "_" + str(id) + ".log"
        print(s)
        return s

    def getNCClientCmd(self, id):
        s = NC.NC_BIN + " " + \
                " -p " + self.ncClientPort[id] + " " + \
                self.mpConfig.getServerIP() + " " + \
                self.ncServerPort + " " + \
                "&>" + NC.CLIENT_NC_LOG + \
                "_" + str(id) + ".log"
        print(s)
        return s

    def clean(self):
        super(NC, self).clean()
        self.mpTopo.commandTo(self.mpConfig.server, "killall netcat")

    def run(self):
        for i in range(0, len(self.ncClientPort)):
            cmd = self.getNCServerCmd(i)
            self.mpConfig.server.sendCmd(cmd)
            
            cmd = self.getNCClientCmd(i)
            self.mpTopo.commandTo(self.mpConfig.client, cmd)

            self.mpConfig.server.waitOutput()
            
            self.mpTopo.commandTo(self.mpConfig.client, "sleep 1")

