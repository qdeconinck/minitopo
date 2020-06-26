from .parameter import Parameter

import logging
import math


class NetemAt(object):
    def __init__(self, at, cmd):
        self.at = at
        self.cmd = cmd
        self.delta = 0

    def __str__(self):
        return "netem at {} ({}) will be {}".format(self.at, self.delta, self.cmd)


class LinkCharacteristics(object):
    """
    Network characteristics associated to a link

    Attributes:
        id              the identifier of the link
        delay           the one-way delay introduced by the link in ms
        queue_size      the size of the link buffer, in packets
        bandwidth       the bandwidth of the link in Mbps
        loss            the random loss rate in percentage
        queuing_delay   the maximum time that a packet can stay in the link buffer (computed over queue_size)
        netem_at        list of NetemAt instances applicable to the link
        backup          integer indicating if this link is a backup one or not (useful for MPTCP)
    """
    def __init__(self, id, delay, queue_size, bandwidth, loss, backup=False):
        self.id = id
        self.delay = delay
        self.queue_size = queue_size
        self.bandwidth = bandwidth
        self.loss = loss
        self.queuing_delay = str(self.extract_queuing_delay(queue_size, bandwidth, delay))
        self.netem_at = []
        self.backup = backup

    def bandwidth_delay_product_divided_by_mtu(self):
        """
        Get the bandwidth-delay product in terms of packets (hence, dividing by the MTU)
        """
        rtt = 2 * float(self.delay)
        """ Since bandwidth is in Mbps and rtt in ms """
        bandwidth_delay_product = (float(self.bandwidth) * 125000.0) * (rtt / 1000.0)
        return int(math.ceil(bandwidth_delay_product * 1.0 / 1500.0))

    def buffer_size(self):
        """
        Return the buffer size in bytes
        """
        return (1500.0 * self.bandwidth_delay_product_divided_by_mtu()) + \
             (float(self.bandwidth) * 1000.0 * float(self.queuing_delay) / 8)

    def extract_queuing_delay(self, queue_size, bandwidth, delay, mtu=1500):
        queuing_delay = (int(queue_size) * int(mtu) * 8.0 * 1000.0) / \
             (float(bandwidth) * 1024 * 1024)
        return max(int(queuing_delay), 1)

    def add_netem_at(self, n):
        if len(self.netem_at) == 0:
            n.delta = n.at
            self.netem_at.append(n)
        else:
            if n.at > self.netem_at[-1].at:
                n.delta = n.at - self.netem_at[-1].at
                self.netem_at.append(n)
            else:
                logging.error("{}: not taken into account because not specified in order in the topo param file".format(n))

    def build_bandwidth_cmd(self, ifname):
        return "&&".join(
            ["sleep {} && tc qdisc del {} root ; tc qdisc add dev {} root handle 5:0 tbf rate {}mbit burst 15000 limit {} ".format(
                n.delta, ifname, ifname, self.bandwidth, self.buffer_size) for n in self.netem_at] + ["true &"]
        )

    def build_netem_cmd(self, ifname):
        return "&&".join(
            ["sleep {} && tc qdisc del deev {} root ; tc qdisc add dev {} root handle 10: netem {} delay {}ms limit 50000 ".format(
                n.delta, ifname, ifname, n.cmd, self.delay) for n in self.netem_at] + ["true &"]
        )

    def build_policing_cmd(self, ifname):
        return "&&".join(
            ["sleep {} && tc qdisc del dev {} ingress ; tc qdisc add dev {} handle ffff: ingress && \
                 tc filter add dev {} parent ffff: u32 match u32 0 0 police rate {}mbit burst {} drop ".format(
                n.delta, ifname, ifname, ifname, self.bandwidth, int(self.buffer_size() * 1.2)) for n in self.netem_at] + ["true &"]
        )

    def as_dict(self):
        return {
            "bw": float(self.bandwidth),
            "delay": "{}ms".format(self.delay),
            "loss": float(self.loss),
            "max_queue_size": int(self.queue_size)
        }

    def __str__(self):
        return """
Link id: {}
    Delay: {}
    Queue Size: {}
    Bandwidth: {}
    Loss: {}
    Backup: {}
        """.format(self.id, self.delay, self.queue_size, self.bandwidth, self.loss, self.backup) + \
            "".join(["\t {} \n".format(n) for n in self.netem_at])


class TopoParameter(Parameter):
    LSUBNET = "leftSubnet"
    RSUBNET = "rightSubnet"
    netem_at = "netem_at_"
    changeNetem = "changeNetem"
    DEFAULT_PARAMETERS = {}
    DEFAULT_PARAMETERS[LSUBNET] = "10.1."
    DEFAULT_PARAMETERS[RSUBNET] = "10.2."
    DEFAULT_PARAMETERS[changeNetem] = "false"

    def __init__(self, parameter_filename):
        Parameter.__init__(self, parameter_filename)
        self.linkCharacteristics = []
        self.loadLinkCharacteristics()
        self.loadNetemAt()
        print(self.__str__())

    def loadNetemAt(self):
        if not self.get(TopoParameter.changeNetem) == "yes":
            return
        for k in sorted(self.parameters):
            if k.startswith(TopoParameter.netem_at):
                i = int(k[len(TopoParameter.netem_at):])
                val = self.parameters[k]
                if not isinstance(val, list):
                    tmp = val
                    val = []
                    val.append(tmp)
                self.loadNetemAtList(i, val)

    def loadNetemAtList(self, id, nlist):
        for n in nlist:
            tab = n.split(",")
            if len(tab)==2:
                o = NetemAt(float(tab[0]), tab[1])
                if id < len(self.linkCharacteristics):
                    self.linkCharacteristics[id].add_netem_at(o)
                else:
                    print("Error can't set netem for link " + str(id))
            else:
                print("Netem wrong line : " + n)
        print(self.linkCharacteristics[id].netem_at)

    def loadLinkCharacteristics(self):
        i = 0
        for k in sorted(self.parameters):
            if k.startswith("path"):
                tab = self.parameters[k].split(",")
                bup = False
                loss = "0.0"
                if len(tab) == 5:
                    loss = tab[3]
                    bup = tab[4] == 'True'
                if len(tab) == 4:
                    try:
                        loss = float(tab[3])
                        loss = tab[3]
                    except ValueError:
                        bup = tab[3] == 'True'
                if len(tab) == 3 or len(tab) == 4 or len(tab) == 5:
                    path = LinkCharacteristics(i,tab[0],
                            tab[1], tab[2], loss, bup)
                    self.linkCharacteristics.append(path)
                    i = i + 1
                else:
                    print("Ignored path :")
                    print(self.parameters[k])

    def get(self, key):
        val = Parameter.get(self, key)
        if val is None:
            if key in TopoParameter.DEFAULT_PARAMETERS:
                return TopoParameter.DEFAULT_PARAMETERS[key]
            else:
                raise Exception("Param not found " + key)
        else:
            return val

    def __str__(self):
        s = Parameter.__str__(self)
        s = s + "\n"
        for p in self.linkCharacteristics[:-1]:
            s = s + p.__str__() + "\n"
        s = s + self.linkCharacteristics[-1].__str__()
        return s

class Topo(object):
    """
    Base class to instantiate a topology.

    This class is not instantiable as it. You must define a child class with the
    `NAME` attribute.
    """
    MININET_BUILDER = "mininet"
    TOPO_ATTR = "topoType"
    switchNamePrefix = "s"
    routerNamePrefix = "r"
    clientName = "Client"
    serverName = "Server"
    routerName = "Router"
    cmdLog = "command.log"

    """Simple MpTopo"""
    def __init__(self, topoBuilder, topoParam):
        self.topoBuilder = topoBuilder
        self.topoParam = topoParam
        self.changeNetem = topoParam.get(TopoParameter.changeNetem)
        self.logFile = open(Topo.cmdLog, 'w')

    def getLinkCharacteristics(self):
        return self.topoParam.linkCharacteristics

    def command_to(self, who, cmd):
        self.logFile.write(who.__str__() + " : " + cmd + "\n")
        return self.topoBuilder.command_to(who, cmd)

    def command_global(self, cmd):
        """
        mainly use for not namespace sysctl.
        """
        self.logFile.write("Not_NS" + " : " + cmd + "\n")
        return self.topoBuilder.command_global(cmd)

    def get_host(self, who):
        return self.topoBuilder.get_host(who)

    def addHost(self, host):
        return self.topoBuilder.addHost(host)

    def addSwitch(self, switch):
        return self.topoBuilder.addSwitch(switch)

    def addLink(self, fromA, toB, **kwargs):
        self.topoBuilder.addLink(fromA,toB,**kwargs)

    def get_cli(self):
        self.topoBuilder.get_cli()

    def start_network(self):
        self.topoBuilder.start_network()

    def closeLogFile(self):
        self.logFile.close()

    def stop_network(self):
        self.topoBuilder.stop_network()


class TopoConfig(object):
    """
    Base class to instantiate a topology.

    This class is not instantiable as it. You must define a child class with the
    `NAME` attribute.
    """

    PING_OUTPUT = "ping.log"

    def __init__(self, topo, param):
        self.topo = topo
        self.param = param

    def configure_network(self):
        print("Configure interfaces....Generic call ?")
        self.configureInterfaces()
        self.configureRoute()

    def disable_tso(self):
        """
        Disable TSO on all interfaces
        """
        links = self.topo.getLinkCharacteristics()
        for i, l in enumerate(links):
            lname = self.getMidLeftName(i)
            rname = self.getMidRightName(i)
            lbox = self.topo.get_host(lname)
            lif = self.getMidL2RInterface(i)
            rif = self.getMidR2LInterface(i)
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

        # And for the server
        cmd = "ethtool -K " + self.getServerInterface() + " tso off"
        print(cmd)
        self.topo.command_to(self.server, cmd)

        cmd = "ethtool -K " + self.get_router_interface_to_switch(self.client_interface_count()) + " tso off"
        print(cmd)
        self.topo.command_to(self.router, cmd)

    def run_netem_at(self):
        """
        Prepare netem commands to be run after some delay
        """
        if not self.topo.changeNetem == "yes":
            # Just rely on defaults of TCLink
            logging.debug("No need to change netem")
            return

        logging.info("Will change netem config on the fly")
        links = self.topo.getLinkCharacteristics()
        for i, l in enumerate(links):
            lname = self.getMidLeftName(i)
            rname = self.getMidRightName(i)
            lbox = self.topo.get_host(lname)
            lif = self.getMidL2RInterface(i)
            rif = self.getMidR2LInterface(i)
            rbox = self.topo.get_host(rname)
            print(str(lname) + " " + str(lif))
            print(str(rname) + " " + str(rif))
            print("boxes " + str(lbox) + " " + str(rbox))
            cmd = l.build_bandwidth_cmd(lif)
            print(cmd)
            self.topo.command_to(lbox, cmd)
            cmd = l.build_bandwidth_cmd(rif)
            print(cmd)
            self.topo.command_to(rbox, cmd)
            ilif = self.getMidL2RIncomingInterface(i)
            irif = self.getMidR2LIncomingInterface(i)
            cmd = l.build_policing_cmd(ilif)
            print(cmd)
            self.topo.command_to(lbox, cmd)
            cmd = l.build_policing_cmd(irif)
            print(cmd)
            self.topo.command_to(rbox, cmd)
            cmd = l.build_netem_cmd(irif)
            print(cmd)
            self.topo.command_to(rbox, cmd)
            cmd = l.build_netem_cmd(ilif)
            print(cmd)
            self.topo.command_to(lbox, cmd)

    def getMidL2RInterface(self, id):
        "get Middle link, left to right interface"
        pass

    def getMidR2LInterface(self, id):
        pass

    def getMidLeftName(self, i):
        "get Middle link, left box name"
        pass

    def getMidRightName(self, i):
        pass

    def configureInterfaces(self):
        pass

    def client_interface_count(self):
        """
        Return the number of client's interfaces
        """
        raise NotImplementedError()

    def get_client_interface(self, index):
        """
        Return the client's interface with index `index`
        """
        raise NotImplementedError()

    def get_router_interface_to_switch(self, index):
        """
        Return the router's interface to switch with index `index`
        """
        raise NotImplementedError()

    def interface_backup_command(self, interfaceName):
        s = "/home/mininet/git/iproute-mptcp/ip/ip link set dev " + interfaceName + " multipath backup "
        print(s)
        return s

    def interfaceUpCommand(self, interfaceName, ip, subnet):
        s = "ifconfig " + interfaceName + " " + ip + " netmask " + \
            subnet
        print(s)
        return s

    def addRouteTableCommand(self, fromIP, id):
        s = "ip rule add from " + fromIP + " table " + str(id + 1)
        print(s)
        return s

    def addRouteScopeLinkCommand(self, network, interfaceName, id):
        s = "ip route add " + network + " dev " + interfaceName + \
                " scope link table " + str(id + 1)
        print(s)
        return s

    def addRouteDefaultCommand(self, via, id):
        s = "ip route add default via " + via + " table " + str(id + 1)
        print(s)
        return s

    def addRouteDefaultGlobalCommand(self, via, interfaceName):
        s = "ip route add default scope global nexthop via " + via + \
                " dev " + interfaceName
        print(s)
        return s

    def arpCommand(self, ip, mac):
        s = "arp -s " + ip + " " + mac
        print(s)
        return s

    def addRouteDefaultSimple(self, via):
        s = "ip route add default via " + via
        print(s)
        return s

    def pingCommand(self, fromIP, toIP, n=5):
        s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
                " >> " + TopoConfig.PING_OUTPUT
        print(s)
        return s
