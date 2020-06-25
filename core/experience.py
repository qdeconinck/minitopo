from .parameter import Parameter
from topos.multi_interface import MultiInterfaceTopo

class ExperienceParameter(Parameter):
    """
    Handler for experience parameters stored in configuration files
    """
    RMEM       = "rmem"
    WMEM       = "wmem"
    SCHED      = "sched"
    CC		   = "congctrl"
    AUTOCORK   = "autocork"
    EARLYRETRANS = "earlyRetrans"
    KERNELPM   = "kpm"
    KERNELPMC  = "kpmc" #kernel path manager client / server
    KERNELPMS  = "kpms"
    USERPMC	   = "upmc"
    USERPMS	   = "upms" #userspace path manager client / server
    USERPMCARGS   = "upmc_args"
    USERPMSARGS   = "upms_args"
    CLIENTPCAP = "clientPcap"
    SERVERPCAP = "serverPcap"
    SNAPLENPCAP = "snaplenPcap"
    XPTYPE     = "xpType"
    PINGCOUNT  = "pingCount"
    NETPERFTESTLEN = "netperfTestlen"
    NETPERFTESTNAME = "netperfTestname"
    NETPERFREQRESSIZE = "netperfReqresSize"
    VLCFILE = "vlcFile"
    VLCTIME = "vlcTime"
    QUICMULTIPATH = "quicMultipath"
    QUICSIRIRUNTIME = "quicSiriRunTime"
    PRIOPATH0 = "prioPath0"
    PRIOPATH1 = "prioPath1"
    BACKUPPATH0 = "backupPath0"
    BACKUPPATH1 = "backupPath1"
    EXPIRATION = "expiration"
    BUFFERAUTOTUNING = "bufferAutotuning"
    METRIC = "metric"


    # Global sysctl keys
    SYSCTL_KEY = {
        RMEM: "net.ipv4.tcp_rmem",
        WMEM: "net.ipv4.tcp_wmem",
        KERNELPM: "net.mptcp.mptcp_path_manager",
        SCHED: "net.mptcp.mptcp_scheduler",
        CC: "net.ipv4.tcp_congestion_control",
        AUTOCORK: "net.ipv4.tcp_autocorking",
        EARLYRETRANS: "net.ipv4.tcp_early_retrans",
        EXPIRATION: "net.mptcp.mptcp_sched_expiration",
        BUFFERAUTOTUNING: "net.ipv4.tcp_moderate_rcvbuf",
    }

    # sysctl keys specific to client and server, independently
    SYSCTL_KEY_CLIENT = {
        KERNELPMC: "net.mptcp.mptcp_path_manager",
    }
    SYSCTL_KEY_SERVER = {
        KERNELPMS: "net.mptcp.mptcp_path_manager",
    }

    # Default values for unspecified experience parameters
    DEFAULT_PARAMETERS = {
        RMEM: "10240 87380 16777216",
        WMEM: "4096 16384 4194304",
        KERNELPM: "fullmesh",
        KERNELPMC: "fullmesh",
        KERNELPMS: "fullmesh",
        USERPMC: "fullmesh",
        USERPMS: "fullmesh",
        USERPMCARGS: "",
        USERPMSARGS: "",
        CC: "olia",
        SCHED: "default",
        AUTOCORK: "1",
        EARLYRETRANS: "3",
        EXPIRATION: "300",
        BUFFERAUTOTUNING: "1",
        METRIC: "-1",
        CLIENTPCAP: "no",
        SERVERPCAP: "no",
        SNAPLENPCAP: "65535",  # Default snapping value of tcpdump
        XPTYPE: "none",
        PINGCOUNT: "5",
        NETPERFTESTLEN: "10",
        NETPERFTESTNAME: "TCP_RR",
        NETPERFREQRESSIZE: "2K,256",
        VLCFILE: "bunny_ibmff_360.mpd",
        VLCTIME: "0",
        QUICMULTIPATH: "0",
        PRIOPATH0: "0",
        PRIOPATH1: "0",
        BACKUPPATH0: "0",
        BACKUPPATH1: "0",
    }

    def __init__(self, parameter_filename):
        super(ExperienceParameter, self).__init__(parameter_filename)
        self.default_parameters = ExperienceParameter.DEFAULT_PARAMETERS

    def get(self, key):
        val = super(ExperienceParameter, self).get(key)
        if val is None:
            if key in self.default_parameters:
                return self.default_parameters[key]
            else:
                raise Exception("Parameter not found " + key)
        else:
            return val


class Experience(object):
    """
	Base class to instantiate an experience to perform.

	This class is not instantiable as it. You must define a child class with the
	`NAME` attribute.

    By default, an Experience relies on an instance of ExperienceParameter to
    collect the parameters from the experience configuration file. However, an
    experience may introduce specific parameters in the configuration file. In
    such case, the inherinting class must override the `PARAMETER_CLASS` class
    variable to point to another class inheriting from ExperienceParameter.

    Attributes:
        experience_parameter    Instance of ExperienceParameter
        topo                    Instance of Topo
        topo_config             Instance of TopoConfig
	"""
    PARAMETER_CLASS = ExperienceParameter

    def __init__(self, experience_parameter_filename, topo, topo_config):
        """
        Instantiation of this base class only load the experience parameter
        """
        self.experience_parameter = self.__class__.PARAMETER_CLASS(experience_parameter_filename)
        self.topo = topo
        self.topo_config = topo_config

    def load_parameters(self):
        """
        Load the parameter of interest from self.experience_parameter
        """
        # Nothing to do in the base class
        pass

    def classic_run(self):
        """
        Default function to perform the experiment. It consists into three phases:
        - A preparation phase through `prepare()` (generating experiment files,...)
        - A running phase through `run()` (where the actual experience takes place)
        - A cleaning phase through `clean()` (stopping traffic, removing generated files,...)
        """
        self.prepare()
        self.run()
        self.clean()

    def prepare(self):
        """
        Prepare the environment to run the experience.
        Typically, when you inherit from this class, you want to extend this
        method, while still calling this parent function.

        TODO: split experience traffic and protocol configuration
        """
        self.setup_sysctl()
        self.run_userspace_path_manager()  # TODO to move elsewhere
        self.topo_config.configure_network()
        self.change_metric()  # TODO to move elsewhere
        self.put_priority_on_paths()  # TODO to move elsewhere
        self.disable_tso()
        self.runTcpDump()
        self.runNetemAt()

    def change_metric(self):
        """
        Function only meaningful for MPTCP and its specific scheduler
        """
        metric = self.experience_parameter.get(ExperienceParameter.METRIC)
        if int(metric) >= 0:
            self.topo.command_global(
                "echo {} > /sys/module/mptcp_sched_metric/parameters/metric".format(metric))

    def put_priority_on_paths(self):
        """
        Function only meaningful for MPTCP
        """
        # Only meaningful if mpTopo is instance of MultiInterfaceTopo
        if isinstance(self.topo, MultiInterfaceTopo):
            prioPath0 = self.experience_parameter.get(ExperienceParameter.PRIOPATH0)
            prioPath1 = self.experience_parameter.get(ExperienceParameter.PRIOPATH1)
            if not prioPath0 == prioPath1:
                self.topo.command_to(self.topo_config.client, "/home/mininet/iproute/ip/ip link set dev " +
                                        self.topo_config.getClientInterface(0) + " priority " + str(prioPath0))
                self.topo.command_to(self.topo_config.router, "/home/mininet/iproute/ip/ip link set dev " +
                                      self.topo_config.getRouterInterfaceSwitch(0) + " priority " +
                                      str(prioPath0))
                self.topo.command_to(self.topo_config.client, "/home/mininet/iproute/ip/ip link set dev " +
                                      self.topo_config.getClientInterface(1) + " priority " + str(prioPath1))
                self.topo.command_to(self.topo_config.router, "/home/mininet/iproute/ip/ip link set dev " +
                                      self.topo_config.getRouterInterfaceSwitch(1) + " priority " +
                                      str(prioPath1))

            backupPath0 = self.experience_parameter.get(ExperienceParameter.BACKUPPATH0)
            if int(backupPath0) > 0:
                self.topo.command_to(self.topo_config.client, self.topo_config.interfaceBUPCommand(self.topo_config.getClientInterface(0)))
                self.topo.command_to(self.topo_config.router, self.topo_config.interfaceBUPCommand(self.topo_config.getRouterInterfaceSwitch(0)))
            backupPath1 = self.experience_parameter.get(ExperienceParameter.BACKUPPATH1)
            if int(backupPath1) > 0:
                self.topo.command_to(self.topo_config.client, self.topo_config.interfaceBUPCommand(self.topo_config.getClientInterface(1)))
                self.topo.command_to(self.topo_config.router, self.topo_config.interfaceBUPCommand(self.topo_config.getRouterInterfaceSwitch(1)))

    def disable_tso(self):
        links = self.topo.getLinkCharacteristics()
        i = 0
        for l in links:
            lname = self.topo_config.getMidLeftName(i)
            rname = self.topo_config.getMidRightName(i)
            lbox = self.topo.get_host(lname)
            lif = self.topo_config.getMidL2RInterface(i)
            rif = self.topo_config.getMidR2LInterface(i)
            rbox = self.topo.get_host(rname)
            print(str(lname) + " " + str(lif))
            print(str(rname) + " " + str(rif))
            print("boxes " + str(lbox) + " " + str(rbox))
            cmd = "ethtool -K " + lif + " tso off"
            print(cmd)
            self.topo.command_to(lbox, cmd)
            cmd = "ethtool -K " + rif + " tso off"
            print(cmd)
            self.topo.command_to(rbox, cmd)
            i = i + 1

        # And for the server
        cmd = "ethtool -K " + self.topo_config.getServerInterface() + " tso off"
        print(cmd)
        self.topo.command_to(self.topo_config.server, cmd)

        cmd = "ethtool -K " + self.topo_config.getRouterInterfaceSwitch(self.topo_config.getClientInterfaceCount()) + " tso off"
        print(cmd)
        self.topo.command_to(self.topo_config.router, cmd)

    def run_userspace_path_manager(self):
        if self.experience_parameter.get(ExperienceParameter.KERNELPMC) != "netlink":
            print("Client : Error, I can't change the userspace pm if the kernel pm is not netlink !")
        else:
            upmc = self.experience_parameter.get(ExperienceParameter.USERPMC)
            upmca = self.experience_parameter.get(ExperienceParameter.USERPMCARGS)
            self.topo.command_to(self.topo_config.client, upmc + \
                    " " + upmca + " &>upmc.log &")
        if self.experience_parameter.get(ExperienceParameter.KERNELPMS) != "netlink":
            print("Server : Error, I can't change the userspace pm if the kernel pm is not netlink !")
        else:
            upms = self.experience_parameter.get(ExperienceParameter.USERPMS)
            upmsa = self.experience_parameter.get(ExperienceParameter.USERPMSARGS)
            self.topo.command_to(self.topo_config.server, upms + \
                    " " + upmsa + " &>upms.log &")

    def cleanUserspacePM(self):
        if self.experience_parameter.get(ExperienceParameter.KERNELPMC) != "netlink":
            print("Client : Error, I can't change the userspace pm if the kernel pm is not netlink !")
        else:
            upmc = self.experience_parameter.get(ExperienceParameter.USERPMC)
            self.topo.command_to(self.topo_config.client, "killall " + upmc)
        if self.experience_parameter.get(ExperienceParameter.KERNELPMS) != "netlink":
            print("Server : Error, I can't change the userspace pm if the kernel pm is not netlink !")
        else:
            upms = self.experience_parameter.get(ExperienceParameter.USERPMS)
            self.topo.command_to(self.topo_config.server, "killall " + upms)

    def runNetemAt(self):
        if not self.topo.changeNetem == "yes":
            print("I don't need to change netem")
            return
        print("Will change netem config on the fly")
        links = self.topo.getLinkCharacteristics()
        i = 0
        for l in links:
            lname = self.topo_config.getMidLeftName(i)
            rname = self.topo_config.getMidRightName(i)
            lbox = self.topo.get_host(lname)
            lif = self.topo_config.getMidL2RInterface(i)
            rif = self.topo_config.getMidR2LInterface(i)
            rbox = self.topo.get_host(rname)
            print(str(lname) + " " + str(lif))
            print(str(rname) + " " + str(rif))
            print("boxes " + str(lbox) + " " + str(rbox))
            cmd = l.buildBwCmd(lif)
            print(cmd)
            self.topo.command_to(lbox, cmd)
            cmd = l.buildBwCmd(rif)
            print(cmd)
            self.topo.command_to(rbox, cmd)
            ilif = self.topo_config.getMidL2RIncomingInterface(i)
            irif = self.topo_config.getMidR2LIncomingInterface(i)
            cmd = l.buildPolicingCmd(ilif)
            print(cmd)
            self.topo.command_to(lbox, cmd)
            cmd = l.buildPolicingCmd(irif)
            print(cmd)
            self.topo.command_to(rbox, cmd)
            cmd = l.buildNetemCmd(irif)
            print(cmd)
            self.topo.command_to(rbox, cmd)
            cmd = l.buildNetemCmd(ilif)
            print(cmd)
            self.topo.command_to(lbox, cmd)

            i = i + 1

    def run(self):
        pass

    def clean(self):
        self.topo.command_to(self.topo_config.client,
                "killall tcpdump")
        self.topo.command_to(self.topo_config.server,
                "killall tcpdump")
        self.backUpSysctl()
        self.cleanUserspacePM()
        pass

    def setup_sysctl(self):
        self.save_sysctl()
        self.write_sysctl()

    def save_sysctl(self):
        self.sysctlBUP = {}
        self._save_sysctl(ExperienceParameter.SYSCTL_KEY, self.sysctlBUP)
        self.sysctlBUPC = {}
        self._save_sysctl(ExperienceParameter.SYSCTL_KEY_CLIENT, self.sysctlBUPC,
                ns = True, who = self.topo_config.client)
        self.sysctlBUPS = {}
        self._save_sysctl(ExperienceParameter.SYSCTL_KEY_SERVER, self.sysctlBUPS,
                ns = True, who = self.topo_config.server)

    def _save_sysctl(self, sysctlDic, sysctlBUP, ns = False, who = None):
        for k in sysctlDic:
            SYSCTL_KEY = sysctlDic[k]
            cmd = self.cmdReadSysctl(SYSCTL_KEY)
            if not ns:
                val = self.topo.command_global(cmd)
            else:
                val = self.topo.command_to(who, cmd)
            if val == "Error":
                print("oooops can't get sysctl " + SYSCTL_KEY)
            else:
                # For Python3 compatibility
                if type(val) is bytes:
                    val = val.decode()
                sysctlBUP[k] = val.split(" ",2)[2][:-1]


    def cmdReadSysctl(self, key):
        s = "sysctl " + key
        return s

    def cmd_write_sysctl(self, key, value):
        s = self.cmdReadSysctl(key)
        s = s + "=\"" + str(value) + "\""
        return s

    def write_sysctl(self):
        self._write_sysctl(ExperienceParameter.SYSCTL_KEY, self.sysctlBUP)
        self._write_sysctl(ExperienceParameter.SYSCTL_KEY_CLIENT, self.sysctlBUPC,
                ns = True, who = self.topo_config.client)
        self._write_sysctl(ExperienceParameter.SYSCTL_KEY_SERVER, self.sysctlBUPS,
                ns = True, who = self.topo_config.server)

    def _write_sysctl(self, sysctlDic, sysctlBUP, ns = False, who = None):
        for k in sysctlBUP:
            SYSCTL_KEY = sysctlDic[k]
            sysctlValue = self.experience_parameter.get(k)
            cmd = self.cmd_write_sysctl(SYSCTL_KEY,sysctlValue)
            if not ns:
                val = self.topo.command_global(cmd)
            else:
                val = self.topo.command_to(who, cmd)
            if val == "Error":
                print("oooops can't set sysctl " + SYSCTL_KEY)


    def backUpSysctl(self):
        self._backUpSysctl(ExperienceParameter.SYSCTL_KEY, self.sysctlBUP)
        self._backUpSysctl(ExperienceParameter.SYSCTL_KEY_CLIENT, self.sysctlBUPC,
                ns = True, who = self.topo_config.client)
        self._backUpSysctl(ExperienceParameter.SYSCTL_KEY_SERVER, self.sysctlBUPS,
                ns = True, who = self.topo_config.server)


    def _backUpSysctl(self, sysctlDic, sysctlBUP, ns = False, who = None):
        for k in sysctlBUP:
            SYSCTL_KEY = sysctlDic[k]
            sysctlValue = sysctlBUP[k]
            cmd = self.cmd_write_sysctl(SYSCTL_KEY,sysctlValue)
            if not ns:
                val = self.topo.command_global(cmd)
            else:
                val = self.topo.command_to(who, cmd)

            if val == "Error":
                print("oooops can't set sysctl " + SYSCTL_KEY)


    def runTcpDump(self):
        #todo : replace filename by cst
        cpcap = self.experience_parameter.get(ExperienceParameter.CLIENTPCAP)
        spcap = self.experience_parameter.get(ExperienceParameter.SERVERPCAP)
        snaplenpcap = self.experience_parameter.get(ExperienceParameter.SNAPLENPCAP)
        if cpcap == "yes" :
            self.topo.command_to(self.topo_config.client,
                    "tcpdump -i any -s " + snaplenpcap + " -w client.pcap &")
        if spcap == "yes" :
            self.topo.command_to(self.topo_config.server,
                    "tcpdump -i any -s " + snaplenpcap + " -w server.pcap &")
        if spcap == "yes" or cpcap == "yes":
            self.topo.command_to(self.topo_config.client,"sleep 5")


class RandomFileParameter(ExperienceParameter):
    """
    Parameters for the RandomFileExperience
    """
    FILE = "file"  # file to fetch; if random, we create a file with random data called random.
    RANDOM_SIZE = "file_size"  # in KB

    def __init__(self, experience_parameter_filename):
        super(RandomFileParameter, self).__init__(experience_parameter_filename)
        self.default_parameters.update({
            RandomFileParameter.FILE: "random",
            RandomFileParameter.RANDOM_SIZE: "1024",
        })

class RandomFileExperience(Experience):
    """
    Enable a experience to use random files

    This class is not directly instantiable
    """
    PARAMETER_CLASS = RandomFileParameter

    def __init__(self, experience_parameter_filename, topo, topo_config):
        super(RandomFileExperience, self).__init__(experience_parameter_filename, topo, topo_config)
        self.load_parameters()
        self.ping()

    def load_parameters(self):
        super(RandomFileExperience, self).load_parameters()
        self.file = self.experience_parameter.get(RandomFileParameter.FILE)
        self.random_size = self.experience_parameter.get(RandomFileParameter.RANDOM_SIZE)

    def prepare(self):
        super(RandomFileExperience, self).prepare()
        if self.file  == "random":
            self.topo.command_to(self.topo_config.client,
                "dd if=/dev/urandom of=random bs=1K count={}".format(self.random_size))

    def clean(self):
        super(RandomFileExperience, self).clean()
        if self.file  == "random":
            self.topo.command_to(self.topo_config.client, "rm random*")
