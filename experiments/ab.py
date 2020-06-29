from core.experiment import RandomFileExperiment, RandomFileParameter, ExperimentParameter
import os


class ABParameter(RandomFileParameter):
    CONCURRENT_REQUESTS = "abConccurentRequests"
    TIME_LIMIT = "abTimelimit"

    def __init__(self, experiment_parameter_filename):
        super(ABParameter, self).__init__(experiment_parameter_filename)
        self.default_parameters.update({
            ABParameter.CONCURRENT_REQUESTS: "50",
            ABParameter.TIME_LIMIT: "20",
        })


class AB(RandomFileExperiment):
    NAME = "ab"
    PARAMETER_CLASS = ABParameter

    SERVER_LOG = "ab_server.log"
    CLIENT_LOG = "ab_client.log"
    AB_BIN = "ab"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(AB, self).__init__(experiment_parameter_filename, topo, topo_config)

    def load_parameters(self):
        super(AB, self).load_parameters()
        self.concurrent_requests = self.experiment_parameter.get(ABParameter.CONCURRENT_REQUESTS)
        self.time_limit = self.experiment_parameter.get(ABParameter.TIME_LIMIT)

    def prepare(self):
        super(AB, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                AB.CLIENT_LOG )
        self.topo.command_to(self.topo_config.server, "rm " + \
                AB.SERVER_LOG )

    def get_ab_server_cmd(self):
        s = "python {}/../utils/http_server.py &> {} 2>&1 &".format(
            os.path.dirname(os.path.abspath(__file__)), AB.SERVER_LOG)
        print(s)
        return s

    def get_ab_client_cmd(self):
        s = "{} -c {} -t {} http://{}/{} &> {}".format(AB.AB_BIN, self.concurrent_requests,
            self.time_limit, self.topo_config.get_server_ip(), self.file, AB.CLIENT_LOG)
        print(s)
        return s

    def clean(self):
        super(AB, self).clean()

    def run(self):
        cmd = self.get_ab_server_cmd()
        self.topo.command_to(self.topo_config.server, cmd)
        print("Wait for the HTTP server to be up, this can take quite a while...")
        self.topo.command_to(self.topo_config.client, "sleep 15")
        cmd = self.get_ab_client_cmd()
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.client, "sleep 2")
