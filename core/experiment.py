from .parameter import Parameter

import logging

class ExperimentParameter(Parameter):
    """
    Handler for experiment parameters stored in configuration files.
    The following parameters are common (and thus usable) by all experiments.
    If you want to add experiement-specific parameters, you should extend this
    class.

    Attribute:
        default_parameters  Default values for the parameters
    """
    RMEM       = "rmem"
    WMEM       = "wmem"
    MPTCP_ENABLED = "mptcpEnabled"
    SCHED      = "sched"
    CC		   = "congctrl"
    AUTOCORK   = "autocork"
    EARLY_RETRANS = "earlyRetrans"
    KERNELPM   = "kpm"
    KERNELPMC  = "kpmc" #kernel path manager client / server
    KERNELPMS  = "kpms"
    USERPMC	   = "upmc"
    USERPMS	   = "upms" #userspace path manager client / server
    USERPMC_ARGS   = "upmc_args"
    USERPMS_ARGS   = "upms_args"
    CLIENT_PCAP = "clientPcap"
    SERVER_PCAP = "serverPcap"
    SNAPLEN_PCAP = "snaplen_pcap"
    XP_TYPE     = "xpType"
    PING_COUNT  = "pingCount"
    PRIO_PATH_0 = "priority_path_0"
    PRIO_PATH_1 = "priority_path_1"
    BACKUP_PATH_0 = "backup_path_0"
    BACKUP_PATH_1 = "backup_path_1"
    BUFFER_AUTOTUNING = "bufferAutotuning"
    METRIC = "metric"

    # Global sysctl keys
    SYSCTL_KEY = {
        RMEM: "net.ipv4.tcp_rmem",
        WMEM: "net.ipv4.tcp_wmem",
        MPTCP_ENABLED: "net.mptcp.mptcp_enabled",
        KERNELPM: "net.mptcp.mptcp_path_manager",
        SCHED: "net.mptcp.mptcp_scheduler",
        CC: "net.ipv4.tcp_congestion_control",
        AUTOCORK: "net.ipv4.tcp_autocorking",
        EARLY_RETRANS: "net.ipv4.tcp_early_retrans",
        BUFFER_AUTOTUNING: "net.ipv4.tcp_moderate_rcvbuf",
    }

    # sysctl keys specific to client and server, independently
    SYSCTL_KEY_CLIENT = {
        KERNELPMC: "net.mptcp.mptcp_path_manager",
    }
    SYSCTL_KEY_SERVER = {
        KERNELPMS: "net.mptcp.mptcp_path_manager",
    }

    # Default values for unspecified experiment parameters
    DEFAULT_PARAMETERS = {
        RMEM: "10240 87380 16777216",
        WMEM: "4096 16384 4194304",
        MPTCP_ENABLED: "1",
        KERNELPM: "fullmesh",
        KERNELPMC: "fullmesh",
        KERNELPMS: "fullmesh",
        USERPMC: "fullmesh",
        USERPMS: "fullmesh",
        USERPMC_ARGS: "",
        USERPMS_ARGS: "",
        CC: "olia",
        SCHED: "default",
        AUTOCORK: "1",
        EARLY_RETRANS: "3",
        BUFFER_AUTOTUNING: "1",
        METRIC: "-1",
        CLIENT_PCAP: "no",
        SERVER_PCAP: "no",
        SNAPLEN_PCAP: "65535",  # Default snapping value of tcpdump
        XP_TYPE: "none",
        PING_COUNT: "5",
        PRIO_PATH_0: "0",
        PRIO_PATH_1: "0",
        BACKUP_PATH_0: "0",
        BACKUP_PATH_1: "0",
    }

    def __init__(self, parameter_filename):
        super(ExperimentParameter, self).__init__(parameter_filename)
        self.default_parameters.update(ExperimentParameter.DEFAULT_PARAMETERS)


class Experiment(object):
    """
	Base class to instantiate an experiment to perform.

	This class is not instantiable as it. You must define a child class with the
	`NAME` attribute.

    By default, an Experiment relies on an instance of ExperimentParameter to
    collect the parameters from the experiment configuration file. However, an
    experiment may introduce specific parameters in the configuration file. In
    such case, the inherinting class must override the `PARAMETER_CLASS` class
    variable to point to another class inheriting from ExperimentParameter.

    Attributes:
        experiment_parameter    Instance of ExperimentParameter
        topo                    Instance of Topo
        topo_config             Instance of TopoConfig
	"""
    PARAMETER_CLASS = ExperimentParameter

    IP_BIN = "ip"
    PING_OUTPUT = "ping.log"

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        """
        Instantiation of this base class only load the experiment parameter
        """
        self.experiment_parameter = self.__class__.PARAMETER_CLASS(experiment_parameter_filename)
        self.topo = topo
        self.topo_config = topo_config

    def load_parameters(self):
        """
        Load the parameter of interest from self.experiment_parameter
        """
        # Nothing to do in the base class
        pass

    def classic_run(self):
        """
        Default function to perform the experiment. It consists into three phases:
        - A preparation phase through `prepare()` (generating experiment files,...)
        - A running phase through `run()` (where the actual experiment takes place)
        - A cleaning phase through `clean()` (stopping traffic, removing generated files,...)
        """
        self.prepare()
        self.run()
        self.clean()

    def prepare(self):
        """
        Prepare the environment to run the experiment.
        Typically, when you inherit from this class, you want to extend this
        method, while still calling this parent function.

        TODO: split experiment traffic and protocol configuration
        """
        self.setup_sysctl()
        self.run_userspace_path_manager()  # TODO to move elsewhere
        self.change_metric()  # TODO to move elsewhere
        self.put_priority_on_paths()  # TODO to move elsewhere
        self.run_tcpdump()
        self.run_netem_at()

    def change_metric(self):
        """
        Function only meaningful for MPTCP and its specific scheduler
        """
        metric = self.experiment_parameter.get(ExperimentParameter.METRIC)
        if int(metric) >= 0:
            self.topo.command_global(
                "echo {} > /sys/module/mptcp_sched_metric/parameters/metric".format(metric))

    def put_priority_on_paths(self):
        """
        Function only meaningful for MPTCP
        """
        priority_path_0 = self.experiment_parameter.get(ExperimentParameter.PRIO_PATH_0)
        priority_path_1 = self.experiment_parameter.get(ExperimentParameter.PRIO_PATH_1)
        if not priority_path_0 == priority_path_1:
            self.topo.command_to(self.topo_config.client, "{} link set dev {} priority {}".format(
                Experiment.IP_BIN, self.topo_config.get_client_interface(0), priority_path_0))
            self.topo.command_to(self.topo_config.router, "{} link set dev {} priority {}".format(
                Experiment.IP_BIN, self.topo_config.get_router_interface_to_client_switch(0), priority_path_0))
            self.topo.command_to(self.topo_config.client, "{} link set dev {} priority {}".format(
                Experiment.IP_BIN, self.topo_config.get_client_interface(1), priority_path_1))
            self.topo.command_to(self.topo_config.router, "{} link set dev {} priority {}".format(
                Experiment.IP_BIN, self.topo_config.get_router_interface_to_client_switch(1), priority_path_1))

        backup_path_0 = self.experiment_parameter.get(ExperimentParameter.BACKUP_PATH_0)
        if int(backup_path_0) > 0:
            self.topo.command_to(self.topo_config.client,
                self.topo_config.interface_backup_command(self.topo_config.get_client_interface(0)))
            self.topo.command_to(self.topo_config.router,
                self.topo_config.interface_backup_command(self.topo_config.get_router_interface_to_client_switch(0)))
        backup_path_1 = self.experiment_parameter.get(ExperimentParameter.BACKUP_PATH_1)
        if int(backup_path_1) > 0:
            self.topo.command_to(self.topo_config.client,
                self.topo_config.interface_backup_command(self.topo_config.get_client_interface(1)))
            self.topo.command_to(self.topo_config.router,
                self.topo_config.interface_backup_command(self.topo_config.get_router_interface_to_client_switch(1)))

    def run_userspace_path_manager(self):
        """
        Function only meaningful to MPTCP with a specific path manager
        """
        if self.experiment_parameter.get(ExperimentParameter.KERNELPMC) == "netlink":
            logging.info("Running user-space path manager on client")
            upmc = self.experiment_parameter.get(ExperimentParameter.USERPMC)
            upmca = self.experiment_parameter.get(ExperimentParameter.USERPMC_ARGS)
            self.topo.command_to(self.topo_config.client, "{} {} &>{} &".format(
                upmc, upmca, "upmc.log"))
        if self.experiment_parameter.get(ExperimentParameter.KERNELPMS) == "netlink":
            logging.info("Running user-space path manager on server")
            upms = self.experiment_parameter.get(ExperimentParameter.USERPMS)
            upmsa = self.experiment_parameter.get(ExperimentParameter.USERPMS_ARGS)
            self.topo.command_to(self.topo_config.server, "{} {} &>{} &".format(
                upms, upmsa, "upms.log"))

    def clean_userspace_path_manager(self):
        if self.experiment_parameter.get(ExperimentParameter.KERNELPMC) == "netlink":
            logging.info("Cleaning user-space path manager on client")
            upmc = self.experiment_parameter.get(ExperimentParameter.USERPMC)
            self.topo.command_to(self.topo_config.client, "killall {}".format(upmc))
        if self.experiment_parameter.get(ExperimentParameter.KERNELPMS) == "netlink":
            logging.info("Cleaning user-space path manager on server")
            upms = self.experiment_parameter.get(ExperimentParameter.USERPMS)
            self.topo.command_to(self.topo_config.client, "killall {}".format(upms))

    def run_netem_at(self):
        self.topo_config.run_netem_at()

    def run(self):
        """
        Perform the experiment

        This function MUST be overriden by child classes
        """
        raise NotImplementedError("Trying to run Experiment")

    def clean(self):
        """
        Clean the environment where the experiment took place.
        Typically, when you inherit from this class, you want to extend this
        method, while still calling this parent function.
        """
        self.topo.command_to(self.topo_config.client, "killall tcpdump")
        self.topo.command_to(self.topo_config.server, "killall tcpdump")
        self.restore_sysctl()
        self.clean_userspace_path_manager()

    def setup_sysctl(self):
        """
        Record the current sysctls of the host and write the experiment ones
        """
        self.save_sysctl()
        self.write_sysctl()

    def save_sysctl(self):
        """
        Record the current sysctls
        """
        self.sysctl_to_restore = {}
        self._save_sysctl(ExperimentParameter.SYSCTL_KEY, self.sysctl_to_restore)
        self.client_sysctl_to_restore = {}
        self._save_sysctl(ExperimentParameter.SYSCTL_KEY_CLIENT, self.client_sysctl_to_restore,
                ns=True, who=self.topo_config.client)
        self.server_sysctl_to_restore = {}
        self._save_sysctl(ExperimentParameter.SYSCTL_KEY_SERVER, self.server_sysctl_to_restore,
                ns=True, who=self.topo_config.server)

    def _save_sysctl(self, sysctl_dict, sysctl_to_restore, ns=False, who=None):
        for k in sysctl_dict:
            sysctl_key = sysctl_dict[k]
            cmd = self.read_sysctl_cmd(sysctl_key)
            if not ns:
                val = self.topo.command_global(cmd)
            else:
                val = self.topo.command_to(who, cmd)
            if val == "Error":
                logging.error("unable to get sysctl {}".format(sysctl_key))
            else:
                # For Python3 compatibility
                if type(val) is bytes:
                    val = val.decode()
                sysctl_to_restore[k] = val.split(" ", 2)[2][:-1]

    def read_sysctl_cmd(self, key):
        """
        Return a bash command to read the sysctl key `key`
        """
        return "sysctl {}".format(key)

    def cmd_write_sysctl(self, key, value):
        """
        Return a bash command to write the sysctl key `key`with value `value`
        """
        return '{}="{}"'.format(self.read_sysctl_cmd(key), value)

    def write_sysctl(self):
        """
        Write the experiment sysctls
        """
        self._write_sysctl(ExperimentParameter.SYSCTL_KEY, self.sysctl_to_restore)
        self._write_sysctl(ExperimentParameter.SYSCTL_KEY_CLIENT, self.client_sysctl_to_restore,
                ns=True, who=self.topo_config.client)
        self._write_sysctl(ExperimentParameter.SYSCTL_KEY_SERVER, self.server_sysctl_to_restore,
                ns=True, who=self.topo_config.server)

    def _write_sysctl(self, sysctl_dict, sysctl_to_restore, ns = False, who = None):
        for k in sysctl_to_restore:
            sysctl_key = sysctl_dict[k]
            sysctl_value = self.experiment_parameter.get(k)
            cmd = self.cmd_write_sysctl(sysctl_key, sysctl_value)
            if not ns:
                val = self.topo.command_global(cmd)
            else:
                val = self.topo.command_to(who, cmd)
            if val == "Error":
                logging.error("unable to set sysctl {}".format(sysctl_key))

    def restore_sysctl(self):
        """
        Restore back the sysctls that were present before running the experiment
        """
        self._restore_sysctl(ExperimentParameter.SYSCTL_KEY, self.sysctl_to_restore)
        self._restore_sysctl(ExperimentParameter.SYSCTL_KEY_CLIENT, self.client_sysctl_to_restore,
                ns=True, who=self.topo_config.client)
        self._restore_sysctl(ExperimentParameter.SYSCTL_KEY_SERVER, self.server_sysctl_to_restore,
                ns=True, who=self.topo_config.server)

    def _restore_sysctl(self, sysctl_dict, sysctl_to_restore, ns = False, who = None):
        for k in sysctl_to_restore:
            sysctl_key = sysctl_dict[k]
            sysctl_value = sysctl_to_restore[k]
            cmd = self.cmd_write_sysctl(sysctl_key, sysctl_value)
            if not ns:
                val = self.topo.command_global(cmd)
            else:
                val = self.topo.command_to(who, cmd)

            if val == "Error":
                logging.error("unable to set sysctl {}".format(sysctl_key))

    def run_tcpdump(self):
        client_pcap = self.experiment_parameter.get(ExperimentParameter.CLIENT_PCAP)
        server_pcap = self.experiment_parameter.get(ExperimentParameter.SERVER_PCAP)
        snaplen_pcap = self.experiment_parameter.get(ExperimentParameter.SNAPLEN_PCAP)
        if client_pcap == "yes":
            self.topo.command_to(self.topo_config.client,
                "tcpdump -i any -s {} -w client.pcap &".format(snaplen_pcap))
        if server_pcap == "yes":
            self.topo.command_to(self.topo_config.server,
                "tcpdump -i any -s {} -w server.pcap &".format(snaplen_pcap))
        if server_pcap == "yes" or client_pcap == "yes":
            logging.info("Activating tcpdump, waiting for it to run")
            self.topo.command_to(self.topo_config.client,"sleep 5")

    def ping(self):
        self.topo.command_to(self.topo_config.client,
                        "rm {}".format(Experiment.PING_OUTPUT))
        count = self.experiment_parameter.get(ExperimentParameter.PING_COUNT)
        for j in range(0, self.topo_config.server_interface_count()):
            for i in range(0, self.topo_config.client_interface_count()):
                cmd = self.ping_command(self.topo_config.get_client_ip(i),
                    self.topo_config.get_server_ip(interface_index=j), n=count)
                logging.info(cmd)
                self.topo.command_to(self.topo_config.client, cmd)

    def ping_command(self, from_ip, to_ip, n=5):
        return "ping -c {} -I {} {} >> {}".format(n, from_ip, to_ip, Experiment.PING_OUTPUT)


class RandomFileParameter(ExperimentParameter):
    """
    Parameters for the RandomFileExperiment
    """
    FILE = "file"  # file to fetch; if random, we create a file with random data called random.
    RANDOM_SIZE = "file_size"  # in KB

    def __init__(self, experiment_parameter_filename):
        super(RandomFileParameter, self).__init__(experiment_parameter_filename)
        self.default_parameters.update({
            RandomFileParameter.FILE: "random",
            RandomFileParameter.RANDOM_SIZE: "1024",
        })


class RandomFileExperiment(Experiment):
    """
    Enable a experiment to use random files

    This class is not directly instantiable
    """
    PARAMETER_CLASS = RandomFileParameter

    def __init__(self, experiment_parameter_filename, topo, topo_config):
        super(RandomFileExperiment, self).__init__(experiment_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()

    def load_parameters(self):
        super(RandomFileExperiment, self).load_parameters()
        self.file = self.experiment_parameter.get(RandomFileParameter.FILE)
        self.random_size = self.experiment_parameter.get(RandomFileParameter.RANDOM_SIZE)

    def prepare(self):
        super(RandomFileExperiment, self).prepare()
        if self.file  == "random":
            self.topo.command_to(self.topo_config.client,
                "dd if=/dev/urandom of=random bs=1K count={}".format(self.random_size))

    def clean(self):
        super(RandomFileExperiment, self).clean()
        if self.file  == "random":
            self.topo.command_to(self.topo_config.client, "rm random*")
