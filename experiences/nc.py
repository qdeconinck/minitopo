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

    def __init__(self, experience_parameter, topo, topo_config):
        super(NC, self).__init__(experience_parameter, topo, topo_config)
        self.loadParam()
        super(NC, self).classic_run()
    
    def loadParam(self):
        self.ddibs = self.experience_parameter.get(ExperienceParameter.DDIBS)
        self.ddobs = self.experience_parameter.get(ExperienceParameter.DDOBS)
        self.ddcount = self.experience_parameter.get(ExperienceParameter.DDCOUNT)
        self.ncServerPort = self.experience_parameter.get(ExperienceParameter.NCSERVERPORT)
        self.ncClientPort = []
        for k in sorted(self.experience_parameter.paramDic):
            if k.startswith(ExperienceParameter.NCCLIENTPORT):
                port = self.experience_parameter.paramDic[k]
                self.ncClientPort.append(port)
        if len(self.ncClientPort) == 0:
            d = self.experience_parameter.get(ExperienceParameter.NCCLIENTPORT)
            self.ncClientPort.append(d)

    def prepare(self):
        super(NC, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                NC.CLIENT_NC_LOG )
        self.topo.command_to(self.topo_config.server, "rm " + \
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
                self.topo_config.getServerIP() + " " + \
                self.ncServerPort + " " + \
                "&>" + NC.CLIENT_NC_LOG + \
                "_" + str(id) + ".log"
        print(s)
        return s

    def clean(self):
        super(NC, self).clean()
        self.topo.command_to(self.topo_config.server, "killall netcat")

    def run(self):
        for i in range(0, len(self.ncClientPort)):
            cmd = self.getNCServerCmd(i)
            self.topo_config.server.sendCmd(cmd)
            
            cmd = self.getNCClientCmd(i)
            self.topo.command_to(self.topo_config.client, cmd)

            self.topo_config.server.waitOutput()
            
            self.topo.command_to(self.topo_config.client, "sleep 1")

