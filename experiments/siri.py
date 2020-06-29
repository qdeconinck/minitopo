from core.experiment import Experiment, ExperimentParameter
import os


class SiriParameter(ExperimentParameter):
    RUN_TIME = "siriRunTime"
    QUERY_SIZE = "siriQuerySize"
    RESPONSE_SIZE = "siriResponseSize"
    DELAY_QUERY_RESPONSE = "siriDelayQueryResponse"
    MIN_PAYLOAD_SIZE = "siriMinPayloadSize"
    MAX_PAYLOAD_SIZE = "siriMaxPayloadSize"
    INTERVAL_TIME_MS = "siriIntervalTimeMs"
    BUFFER_SIZE = "siriBufferSize"
    BURST_SIZE = "siriBurstSize"
    INTERVAL_BURST_TIME_MS = "siriIntervalBurstTimeMs"

    def __init__(self, experiment_parameter_filename):
        super(SiriParameter, self).__init__(experiment_parameter_filename)
        self.default_parameters.update({
            SiriParameter.QUERY_SIZE: "2500",
            SiriParameter.RESPONSE_SIZE: "750",
            SiriParameter.DELAY_QUERY_RESPONSE: "0",
            SiriParameter.MIN_PAYLOAD_SIZE: "85",
            SiriParameter.MAX_PAYLOAD_SIZE: "500",
            SiriParameter.INTERVAL_TIME_MS: "333",
            SiriParameter.BUFFER_SIZE: "9",
            SiriParameter.BURST_SIZE: "0",
            SiriParameter.INTERVAL_BURST_TIME_MS: "0",
        })


class Siri(Experiment):
    NAME = "siri"
    PARAMETER_CLASS = SiriParameter

    SERVER_LOG = "siri_server.log"
    CLIENT_LOG = "siri_client.log"
    CLIENT_ERR = "siri_client.err"
    JAVA_BIN = "java"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(Siri, self).__init__(experiment_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                Siri.PING_OUTPUT )
        count = self.experiment_parameter.get(ExperimentParameter.PING_COUNT)
        for i in range(0, self.topo_config.client_interface_count()):
             cmd = self.ping_command(self.topo_config.get_client_ip(i),
                 self.topo_config.get_server_ip(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def ping_command(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + Siri.PING_OUTPUT
        print(s)
        return s

    def load_parameters(self):
        self.run_time = self.experiment_parameter.get(SiriParameter.RUN_TIME)
        self.query_size = self.experiment_parameter.get(SiriParameter.QUERY_SIZE)
        self.response_size = self.experiment_parameter.get(SiriParameter.RESPONSE_SIZE)
        self.delay_query_response = self.experiment_parameter.get(SiriParameter.DELAY_QUERY_RESPONSE)
        self.min_payload_size = self.experiment_parameter.get(SiriParameter.MIN_PAYLOAD_SIZE)
        self.max_payload_size = self.experiment_parameter.get(SiriParameter.MAX_PAYLOAD_SIZE)
        self.interval_time_ms = self.experiment_parameter.get(SiriParameter.INTERVAL_TIME_MS)
        self.buffer_size = self.experiment_parameter.get(SiriParameter.BUFFER_SIZE)
        self.burst_size = self.experiment_parameter.get(SiriParameter.BURST_SIZE)
        self.interval_burst_time_ms = self.experiment_parameter.get(SiriParameter.INTERVAL_BURST_TIME_MS)

    def prepare(self):
        super(Siri, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                Siri.CLIENT_LOG)
        self.topo.command_to(self.topo_config.server, "rm " + \
                Siri.SERVER_LOG)

    def get_siri_server_cmd(self):
        s = "python3 {}/../utils/siri_server.py &> {}&".format(
            os.path.dirname(os.path.abspath(__file__)), Siri.SERVER_LOG)
        print(s)
        return s

    def get_siri_client_cmd(self):
        s = "{} -jar {}/../utils/siriClient.jar {} 8080 {} {} {} {} {} {} {} {} {} {} > {} 2> {}".format(
            Siri.JAVA_BIN, os.path.dirname(os.path.abspath(__file__)), self.topo_config.get_server_ip(),
            self.run_time, self.query_size, self.response_size, self.delay_query_response,
            self.min_payload_size, self.max_payload_size, self.interval_time_ms, self.buffer_size,
            self.burst_size, self.interval_burst_time_ms, Siri.CLIENT_LOG, Siri.CLIENT_ERR)
        print(s)
        return s

    def clean(self):
        super(Siri, self).clean()

    def run(self):
        cmd = self.get_siri_server_cmd()
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_before")
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        cmd = self.get_siri_client_cmd()
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_before")
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_after")
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_after")
        self.topo.command_to(self.topo_config.server, "pkill -f siri_server.py")
        self.topo.command_to(self.topo_config.client, "sleep 2")
