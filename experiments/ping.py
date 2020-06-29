from core.experiment import Experiment, ExperimentParameter

class Ping(Experiment):
    NAME = "ping"

    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(Ping, self).__init__(experiment_parameter_filename, topo, topo_config)

    def prepare(self):
        super(Ping, self).prepare()

    def clean(self):
        super(Ping, self).clean()

    def run(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                Ping.PING_OUTPUT )
        count = self.experiment_parameter.get(ExperimentParameter.PING_COUNT)
        for i in range(0, self.topo_config.client_interface_count()):
             cmd = self.ping_command(self.topo_config.get_client_ip(i),
                 self.topo_config.get_server_ip(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def ping_command(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + Ping.PING_OUTPUT
        print(s)
        return s
