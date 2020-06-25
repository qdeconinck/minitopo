from .parameter import ExperienceParameter
from topos.multi_interface import MultiInterfaceTopo

class Experience(object):
    """
	Base class to instantiate an experience to perform.

	This class is not instantiable as it. You must define a child class with the
	`NAME` attribute.

    Attributes:
        experience_parameter    Instance of ExperienceParameter
        topo                    Instance of Topo
        topo_config             Instance of TopoConfig
	"""

    def __init__(self, experience_parameter, topo, topo_config):
        self.experience_parameter = experience_parameter
        self.topo = topo
        self.topo_config = topo_config

    def classic_run(self):
        """
        Default function to perform the experiment. It consists into three phases:
        - A preparation phase through `prepare()` (generating experiment files,...)
        - A running phase through `run()` (where the actual experience takes place)
        - A cleaning phase through `clean()` (stopping traffic, removing generated files,...)

        Typically, this function is called in the constructor of child classes.
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
        self._save_sysctl(ExperienceParameter.sysctlKey, self.sysctlBUP)
        self.sysctlBUPC = {}
        self._save_sysctl(ExperienceParameter.sysctlKeyClient, self.sysctlBUPC,
                ns = True, who = self.topo_config.client)
        self.sysctlBUPS = {}
        self._save_sysctl(ExperienceParameter.sysctlKeyServer, self.sysctlBUPS,
                ns = True, who = self.topo_config.server)

    def _save_sysctl(self, sysctlDic, sysctlBUP, ns = False, who = None):
        for k in sysctlDic:
            sysctlKey = sysctlDic[k]
            cmd = self.cmdReadSysctl(sysctlKey)
            if not ns:
                val = self.topo.command_global(cmd)
            else:
                val = self.topo.command_to(who, cmd)
            if val == "Error":
                print("oooops can't get sysctl " + sysctlKey)
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
        self._write_sysctl(ExperienceParameter.sysctlKey, self.sysctlBUP)
        self._write_sysctl(ExperienceParameter.sysctlKeyClient, self.sysctlBUPC,
                ns = True, who = self.topo_config.client)
        self._write_sysctl(ExperienceParameter.sysctlKeyServer, self.sysctlBUPS,
                ns = True, who = self.topo_config.server)

    def _write_sysctl(self, sysctlDic, sysctlBUP, ns = False, who = None):
        for k in sysctlBUP:
            sysctlKey = sysctlDic[k]
            sysctlValue = self.experience_parameter.get(k)
            cmd = self.cmd_write_sysctl(sysctlKey,sysctlValue)
            if not ns:
                val = self.topo.command_global(cmd)
            else:
                val = self.topo.command_to(who, cmd)
            if val == "Error":
                print("oooops can't set sysctl " + sysctlKey)


    def backUpSysctl(self):
        self._backUpSysctl(ExperienceParameter.sysctlKey, self.sysctlBUP)
        self._backUpSysctl(ExperienceParameter.sysctlKeyClient, self.sysctlBUPC,
                ns = True, who = self.topo_config.client)
        self._backUpSysctl(ExperienceParameter.sysctlKeyServer, self.sysctlBUPS,
                ns = True, who = self.topo_config.server)


    def _backUpSysctl(self, sysctlDic, sysctlBUP, ns = False, who = None):
        for k in sysctlBUP:
            sysctlKey = sysctlDic[k]
            sysctlValue = sysctlBUP[k]
            cmd = self.cmd_write_sysctl(sysctlKey,sysctlValue)
            if not ns:
                val = self.topo.command_global(cmd)
            else:
                val = self.topo.command_to(who, cmd)

            if val == "Error":
                print("oooops can't set sysctl " + sysctlKey)


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
