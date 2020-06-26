from core.experiment import ExperimentParameter
from .siri import Siri, SiriParameter
from .msg import Msg, MsgParameter
import os


class SiriMsgParameter(SiriParameter, MsgParameter):
    """
    This class is needed because Python has no way to know what we prefer over Siri or
    Msg parameters. So explicitly state that we want both.
    """
    pass


class SiriMsg(Siri, Msg):
    NAME = "sirimsg"
    PARAMETER_CLASS = SiriMsgParameter

    MSG_SERVER_LOG = "msg_server.log"
    MSG_CLIENT_LOG = "msg_client.log"
    MSG_CLIENT_ERR = "msg_client.err"
    SERVER_LOG = "siri_server.log"
    CLIENT_LOG = "siri_client.log"
    CLIENT_ERR = "siri_client.err"
    JAVA_BIN = "java"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(SiriMsg, self).__init__(experiment_parameter_filename, topo, topo_config)

    def load_parameters(self):
        # Fetch both Msg and Siri parameters
        Siri.load_parameters(self)
        Msg.load_parameters(self)

    def prepare(self):
        # Should be the combination of Siri and Msg
        Siri.prepare(self)
        Msg.prepare(self)

    def clean(self):
        # Should be the combination of Siri and Msg
        Siri.clean(self)
        Msg.clean(self)

    def run(self):
        cmd = self.get_siri_server_cmd()
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_before")
        self.topo.command_to(self.topo_config.server, cmd)
        cmd = self.get_msg_server_cmd()
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_before")
        cmd = self.get_msg_client_cmd(daemon=True)
        self.topo.command_to(self.topo_config.client, cmd)
        cmd = self.get_siri_client_cmd()
        self.topo.command_to(self.topo_config.client, cmd)
        self.topo.command_to(self.topo_config.server, "netstat -sn > netstat_server_after")
        self.topo.command_to(self.topo_config.client, "netstat -sn > netstat_client_after")
        self.topo.command_to(self.topo_config.server, "pkill -f siri_server.py")
        self.topo.command_to(self.topo_config.server, "pkill -f msg_server.py")
        self.topo.command_to(self.topo_config.server, "pkill -f msg_client.py")
        self.topo.command_to(self.topo_config.client, "sleep 2")
