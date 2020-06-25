from core.experience import Experience, ExperienceParameter

class Ping(Experience):
    NAME = "ping"

    PING_OUTPUT = "ping.log"

    def __init__(self, experience_parameter_filename, topo, topo_config):
        super(Ping, self).__init__(experience_parameter_filename, topo, topo_config)
        super(Ping, self).classic_run()

    def prepare(self):
        super(Ping, self).prepare()

    def clean(self):
        super(Ping, self).clean()

    def run(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                Ping.PING_OUTPUT )
        count = self.experience_parameter.get(ExperienceParameter.PINGCOUNT)
        for i in range(0, self.topo_config.getClientInterfaceCount()):
             cmd = self.pingCommand(self.topo_config.getClientIP(i),
                 self.topo_config.getServerIP(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + Ping.PING_OUTPUT
        print(s)
        return s
