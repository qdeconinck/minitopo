from core.experiment import Experiment, ExperimentParameter
import os


class VLCParameter(ExperimentParameter):
    FILE = "vlcFile"
    TIME = "vlcTime"

    def __init__(self, experiment_parameter_filename):
        super(VLCParameter, self).__init__(experiment_parameter_filename)
        self.default_parameters.update({
            VLCParameter.FILE: "bunny_ibmff_360.mpd",
            VLCParameter.TIME: "0",
        })

class VLC(Experiment):
    NAME = "vlc"

    SERVER_LOG = "vlc_server.log"
    CLIENT_LOG = "vlc_client.log"
    VLC_BIN = "/home/mininet/vlc/vlc"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(VLC, self).__init__(experiment_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()

    def ping(self):
        self.topo.command_to(self.topo_config.client, "rm " + \
                VLC.PING_OUTPUT )
        count = self.experiment_parameter.get(ExperimentParameter.PING_COUNT)
        for i in range(0, self.topo_config.client_interface_count()):
             cmd = self.ping_command(self.topo_config.get_client_ip(i),
                 self.topo_config.get_server_ip(), n = count)
             self.topo.command_to(self.topo_config.client, cmd)

    def ping_command(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                  " >> " + VLC.PING_OUTPUT
        print(s)
        return s

    def load_parameters(self):
        self.file = self.experiment_parameter.get(VLCParameter.FILE)
        self.time = self.experiment_parameter.get(VLCParameter.TIME)

    def prepare(self):
        super(VLC, self).prepare()
        self.topo.command_to(self.topo_config.client, "rm " + \
                VLC.CLIENT_LOG )
        self.topo.command_to(self.topo_config.client, "Xvfb :66 &")
        self.topo.command_to(self.topo_config.server, "rm " + \
                VLC.SERVER_LOG )

    def get_vlc_server_cmd(self):
        s = "/etc/init.d/apache2 restart &> {}".format(VLC.SERVER_LOG)
        print(s)
        return s

    def get_vlc_client_cmd(self):
        s = "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/mininet/usr/lib/ && sudo ldconfig && \
            {} -I dummy --x11-display :66 --adaptive-logic 3 --no-loop --play-and-exit \
                http://{}/{} 2>&1 | grep -E '(Neb|halp|bandwidth|late|Buffering|buffering)' > {} {}".format(
                    VLC.VLC_BIN, self.topo_config.get_server_ip(), self.file, VLC.CLIENT_LOG,
                    "&" if self.time != "0" else "")
        print(s)
        return s

    def clean(self):
        super(VLC, self).clean(self)
        self.topo.command_to(self.topo_config.client, "pkill Xvfb")

    def run(self):
        cmd = self.get_vlc_server_cmd()
        self.topo.command_to(self.topo_config.server, cmd)

        self.topo.command_to(self.topo_config.client, "sleep 1")
        cmd = self.get_vlc_client_cmd()
        self.topo.command_to(self.topo_config.client, cmd)

        if self.time != "0" :
            self.topo.command_to(self.topo_config.client, "sleep " + self.time)
            self.topo.command_to(self.topo_config.client, "pkill -9 -f vlc")

        self.topo.command_to(self.topo_config.client, "sleep 2")
