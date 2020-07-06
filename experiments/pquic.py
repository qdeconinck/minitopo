from core.experiment import Experiment, ExperimentParameter
import logging
import os


class PQUICParameter(RandomFileExperiment):
    PLUGINS = "pquicPlugins"
    SIZE = "pquicSize"

    def __init__(self, experiment_parameter_filename):
        super(PQUICParameter, self).__init__(experiment_parameter_filename)
        self.default_parameters.update({
            PQUICParameter.PLUGINS: "",
            PQUICParameter.SIZE: 1024000,
        })


class PQUIC(RandomFileExperiment):
    NAME = "pquic"
    PARAMETER_CLASS = PQUICParameter

    BIN = "~/picoquic/picoquicdemo"
    SERVER_LOG = "pquic_server.log"
    CLIENT_LOG = "pquic_client.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(PQUIC, self).__init__(experiment_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()

    def load_parameters(self):
        super(PQUIC, self).load_parameters()
        self.plugins = self.experiment_parameter.get(PQUICParameter.PLUGINS)
        self.size = int(self.experiment_parameter.get(PQUICParameter.SIZE))

    def prepare(self):
        super(PQUIC, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm {}".format(PQUIC.CLIENT_LOG))
        self.topo.command_to(self.topo_config.server, "rm {}".format(PQUIC.SERVER_LOG))

    def get_plugin_cmd(self):
        if len(self.plugins) == 0:
            return ""

        plugins = self.plugins.split(",")
        return " ".join([" -P {} ".format(p) for p in plugins])

    def get_pquic_server_cmd(self):
        s = "{} {} &> {} &".format(PQUIC.BIN, self.get_plugin_cmd(), PQUIC.SERVER_LOG)
        logging.info(s)
        return s

    def get_pquic_client_cmd(self):
        s = "{} {} -4 -G {} {} 4443 &> {}".format(PQUIC.BIN, self.get_plugin_cmd(), self.size,
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
