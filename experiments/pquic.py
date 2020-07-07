from core.experiment import Experiment, ExperimentParameter
import logging
import os


class PQUICParameter(ExperimentParameter):
    PLUGINS = "pquicPlugins"
    CLIENT_PLUGINS = "pquicClientPlugins"
    SERVER_PLUGINS = "pquicServerPlugins"
    SIZE = "pquicSize"

    def __init__(self, experiment_parameter_filename):
        super(PQUICParameter, self).__init__(experiment_parameter_filename)
        self.default_parameters.update({
            PQUICParameter.PLUGINS: "",
            PQUICParameter.CLIENT_PLUGINS: "",
            PQUICParameter.SERVER_PLUGINS: "",
            PQUICParameter.SIZE: 10240000,
        })


class PQUIC(Experiment):
    NAME = "pquic"
    PARAMETER_CLASS = PQUICParameter

    BIN = "~/pquic/picoquicdemo"
    CERT_FILE = "~/pquic/certs/cert.pem"
    KEY_FILE = "~/pquic/certs/key.pem"
    SERVER_LOG = "pquic_server.log"
    CLIENT_LOG = "pquic_client.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(PQUIC, self).__init__(experiment_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()

    def load_parameters(self):
        super(PQUIC, self).load_parameters()
        self.plugins = self.experiment_parameter.get(PQUICParameter.PLUGINS)
        self.client_plugins = self.experiment_parameter.get(PQUICParameter.CLIENT_PLUGINS)
        self.server_plugins = self.experiment_parameter.get(PQUICParameter.SERVER_PLUGINS)
        self.size = int(self.experiment_parameter.get(PQUICParameter.SIZE))

    def prepare(self):
        super(PQUIC, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm {}".format(PQUIC.CLIENT_LOG))
        self.topo.command_to(self.topo_config.server, "rm {}".format(PQUIC.SERVER_LOG))

    def get_plugin_cmd(self, client=False):
        device_plugins = self.client_plugins if client else self.server_plugins
        device_plugins = self.plugins if len(device_plugins) == 0 else device_plugins
        if len(device_plugins) == 0:
            return ""

        plugins = device_plugins.split(",")
        return " ".join([" -P {} ".format(p) for p in plugins])

    def get_pquic_server_cmd(self):
        s = "{} {} -c {} -k {} &> {} &".format(PQUIC.BIN, self.get_plugin_cmd(),
            PQUIC.CERT_FILE, PQUIC.KEY_FILE, PQUIC.SERVER_LOG)
        logging.info(s)
        return s

    def get_pquic_client_cmd(self):
        s = "{} {} -4 -G {} {} 4443 &> {}".format(PQUIC.BIN, self.get_plugin_cmd(client=True), self.size,
            self.topo_config.get_server_ip(), PQUIC.CLIENT_LOG)
        logging.info(s)
        return s

    def clean(self):
        super(PQUIC, self).clean()

    def run(self):
        cmd = self.get_pquic_server_cmd()
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")

        cmd = self.get_pquic_client_cmd()
        self.topo.command_to(self.topo_config.client, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 2")
