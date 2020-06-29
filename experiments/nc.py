from core.experiment import Experiment, ExperimentParameter

"""
Should be the mother of ExperimentNCPV, shame on me, should rewrite
ExperimentNCPV as daughter class of this one.
"""

class NCParameter(ExperimentParameter):
    DD_IBS      = "ddIBS"
    DD_OBS      = "ddIBS"
    DD_COUNT    = "ddCount"
    SERVER_PORT = "ncServerPort"
    CLIENT_PORT = "ncClientPort"

    def __init__(self, experiment_parameter_filename):
        super(NCParameter, self).__init__(experiment_parameter_filename)
        self.default_parameters.update({
            NCParameter.DD_IBS: "1k",
            NCParameter.DD_OBS: "1k",
            NCParameter.DD_COUNT: "5000", #5k * 1k = 5m
            NCParameter.SERVER_PORT: "33666",
            NCParameter.CLIENT_PORT: "33555",
        })
    

class NC(Experiment):
    NAME = "nc"
    PARAMETER_CLASS = NCParameter

    SERVER_NC_LOG = "netcat_server"
    CLIENT_NC_LOG = "netcat_client"
    NC_BIN = "netcat"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(NC, self).__init__(experiment_parameter_filename, topo, topo_config)
        self.load_parameters()
    
    def load_parameters(self):
        self.ddibs = self.experiment_parameter.get(NCParameter.DD_IBS)
        self.ddobs = self.experiment_parameter.get(NCParameter.DD_OBS)
        self.ddcount = self.experiment_parameter.get(NCParameter.DD_COUNT)
        self.ncServerPort = self.experiment_parameter.get(NCParameter.SERVER_PORT)
        self.ncClientPort = []
        for k in sorted(self.experiment_parameter.paramDic):
            if k.startswith(NCParameter.CLIENT_PORT):
                port = self.experiment_parameter.paramDic[k]
                self.ncClientPort.append(port)
        if len(self.ncClientPort) == 0:
            d = self.experiment_parameter.get(NCParameter.CLIENT_PORT)
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
                self.topo_config.get_server_ip() + " " + \
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

