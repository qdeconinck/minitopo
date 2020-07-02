from core.experiment import Experiment, ExperimentParameter
import logging
import os


class MsgParameter(ExperimentParameter):
    CLIENT_SLEEP = "msgClientSleep"
    SERVER_SLEEP = "msgServerSleep"
    NB_REQUESTS = "msgNbRequests"
    BYTES = "msgBytes"

    def __init__(self, experiment_parameter_filename):
        super(MsgParameter, self).__init__(experiment_parameter_filename)
        self.default_parameters.update({
            MsgParameter.CLIENT_SLEEP: "5.0",
            MsgParameter.SERVER_SLEEP: "5.0",
            MsgParameter.NB_REQUESTS: "5",
            MsgParameter.BYTES: "1200",
        })

class Msg(Experiment):
    NAME = "msg"
    PARAMETER_CLASS = MsgParameter

    SERVER_LOG = "msg_server.log"
    CLIENT_LOG = "msg_client.log"
    CLIENT_ERR = "msg_client.err"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(Msg, self).__init__(experiment_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()

    def load_parameters(self):
        self.client_sleep = self.experiment_parameter.get(MsgParameter.CLIENT_SLEEP)
        self.server_sleep = self.experiment_parameter.get(MsgParameter.SERVER_SLEEP)
        self.nb_requests = self.experiment_parameter.get(MsgParameter.NB_REQUESTS)
        self.bytes = self.experiment_parameter.get(MsgParameter.BYTES)

    def prepare(self):
        super(Msg, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                Msg.CLIENT_LOG)
        self.topo.command_to(self.topo_config.server, "rm " + \
                Msg.SERVER_LOG)

    def get_msg_server_cmd(self):
        s = "python {}/../utils/msg_server.py --sleep {} --bytes {} &> {}&".format(
           os.path.dirname(os.path.abspath(__file__)), self.server_sleep, self.bytes,
           Msg.SERVER_LOG)
        logging.info(s)
        return s

    def get_msg_client_cmd(self, daemon=False):
        s = "python {}/../utils/msg_client.py --sleep {} --nb {} --bytes {} > {} 2> {} {}".format(
           os.path.dirname(os.path.abspath(__file__)), self.client_sleep, self.nb_requests,
           self.bytes, Msg.CLIENT_LOG, Msg.CLIENT_ERR, "&" if daemon else "")
        logging.info(s)
        return s

    def clean(self):
        super(Msg, self).clean()

    def run(self):
        cmd = self.get_msg_server_cmd()
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_before")
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        cmd = self.get_msg_client_cmd()
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_before")
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_after")
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_after")
        self.topo.command_to(self.topo_config.server, "pkill -f msg_server.py")
        self.topo.command_to(self.topo_config.client, "sleep 2")
