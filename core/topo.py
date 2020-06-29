from .parameter import Parameter

import logging
import math


class NetemAt(object):
    """
    Class representing a netem command to be run after some time
    """
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
    LEFT_SUBNET = "leftSubnet"
    RIGHT_SUBNET = "rightSubnet"
    NETEM_AT = "netem_at_"
    CHANGE_NETEM = "changeNetem"

    DEFAULT_PARAMETERS = {
        LEFT_SUBNET: "10.1.",
        RIGHT_SUBNET: "10.2.",
        CHANGE_NETEM: "false",
    }

    def __init__(self, parameter_filename):
        Parameter.__init__(self, parameter_filename)
        self.default_parameters.update(TopoParameter.DEFAULT_PARAMETERS)
        self.link_characteristics = []
        self.load_link_characteristics()
        self.load_netem_at()
        logging.info(self)

    def load_netem_at(self):
        if not self.get(TopoParameter.CHANGE_NETEM) == "yes":
            return
        for k in sorted(self.parameters):
            if k.startswith(TopoParameter.NETEM_AT):
                link_id = int(k[len(TopoParameter.NETEM_AT):])
                val = self.parameters[k]
                if not isinstance(val, list):
                    tmp = val
                    val = []
                    val.append(tmp)
                self.load_netem_at_list(link_id, val)

    def load_netem_at_list(self, link_id, nlist):
        for n in nlist:
            try:
                at, cmd = n.split(",")
                na = NetemAt(float(at), cmd)
                if link_id < len(self.link_characteristics):
                    self.link_characteristics[id].add_netem_at(na)
                else:
                    logging.error("Unable to set netem for link {}; only have {} links".format(
                        link_id, len(self.link_characteristics)))
            except ValueError as e:
                logging.error("Unable to set netem for link {}: {}".format(link_id, n))

        logging.info(self.link_characteristics[link_id].netem_at)

    def load_link_characteristics(self):
        """
        CAUTION: the path_i in config file is not taken into account. Hence place them in
        increasing order in the topo parameter file!
        """
        i = 0
        for k in sorted(self.parameters):
            # TODO FIXME rewrite this function
            if k.startswith("path"):
                tab = self.parameters[k].split(",")
                bup = False
                loss = "0.0"
                if len(tab) == 5:
                    loss = tab[3]
                    bup = tab[4].lower() == 'true'
                if len(tab) == 4:
                    try:
                        loss = float(tab[3])
                        loss = tab[3]
                    except ValueError:
                        bup = tab[3].lower() == 'true'
                if len(tab) == 3 or len(tab) == 4 or len(tab) == 5:
                    path = LinkCharacteristics(i, tab[0],
                            tab[1], tab[2], loss, bup)
                    self.link_characteristics.append(path)
                    i = i + 1
                else:
                    logging.warning("Ignored path {}".format(self.parameters[k]))

    def __str__(self):
        s = "{}".format(super(TopoParameter, self).__str__())
        s += "".join(["{}".format(lc) for lc in self.link_characteristics])
        return s

class Topo(object):
    """
    Base class to instantiate a topology.

    This class is not instantiable as it. You must define a child class with the
    `NAME` attribute.

    Attributes:
        topo_builder    instance of TopoBuilder
        topo_parameter  instance of TopoParameter
        change_netem    boolean indicating if netem must be changed
        log_file        file descriptor logging commands relative to the topo
    """
    MININET_BUILDER = "mininet"
    TOPO_ATTR = "topoType"
    SWITCH_NAME_PREFIX = "s"
    ROUTER_NAME_PREFIX = "r"
    CLIENT_NAME = "Client"
    SERVER_NAME = "Server"
    ROUTER_NAME = "Router"
    CMD_LOG_FILENAME = "command.log"

    def __init__(self, topo_builder, topo_parameter):
        self.topo_builder = topo_builder
        self.topo_parameter = topo_parameter
        self.change_netem = topo_parameter.get(TopoParameter.CHANGE_NETEM).lower() == "yes"
        self.log_file = open(Topo.CMD_LOG_FILENAME, 'w')

    def get_link_characteristics(self):
        return self.topo_parameter.link_characteristics

    def command_to(self, who, cmd):
        self.log_file.write("{} : {}\n".format(who, cmd))
        return self.topo_builder.command_to(who, cmd)

    def command_global(self, cmd):
        """
        mainly use for not namespace sysctl.
        """
        self.log_file.write("Global : {}\n".format(cmd))
        return self.topo_builder.command_global(cmd)

    def get_host(self, who):
        return self.topo_builder.get_host(who)

    def add_host(self, host):
        return self.topo_builder.add_host(host)

    def add_switch(self, switch):
        return self.topo_builder.add_switch(switch)

    def add_link(self, from_a, to_b, **kwargs):
        self.topo_builder.add_link(from_a, to_b, **kwargs)

    def get_cli(self):
        self.topo_builder.get_cli()

    def start_network(self):
        self.topo_builder.start_network()

    def close_log_file(self):
        self.log_file.close()

    def stop_network(self):
        self.topo_builder.stop_network()


class TopoConfig(object):
    """
    Base class to instantiate a topology.

    This class is not instantiable as it. You must define a child class with the
    `NAME` attribute.
    """
    def __init__(self, topo, param):
        self.topo = topo
        self.param = param

    def configure_network(self):
        logging.debug("Configure network in TopoConfig")
        self.configure_interfaces()
        self.configure_routing()

    def disable_tso(self):
        """
        Disable TSO on all interfaces
        """
        links = self.topo.get_link_characteristics()
        for i, l in enumerate(links):
            lbox = self.topo.get_host(self.getMidLeftName(i))
            rbox = self.topo.get_host(self.getMidRightName(i))
            lif = self.getMidL2RInterface(i)
            rif = self.getMidR2LInterface(i)
            logging.info("Disable TSO on link between {} and {}".format(lif, rif))
            cmd = "ethtool -K {} tso off".format(lif)
            logging.info(cmd)
            self.topo.command_to(lbox, cmd)
            cmd = "ethtool -K {} tso off".format(rif)
            logging.info(cmd)
            self.topo.command_to(rbox, cmd)

        # And for the server
        cmd = "ethtool -K {} tso off".format(self.get_server_interface())
        logging.info(cmd)
        self.topo.command_to(self.server, cmd)

        cmd = "ethtool -K {} tso off".format(self.get_router_interface_to_switch(self.client_interface_count()))
        logging.info(cmd)
        self.topo.command_to(self.router, cmd)

    def run_netem_at(self):
        """
        Prepare netem commands to be run after some delay
        """
        if not self.topo.change_netem:
            # Just rely on defaults of TCLink
            logging.info("No need to change netem")
            return

        logging.info("Will change netem config on the fly")
        links = self.topo.get_link_characteristics()
        for i, l in enumerate(links):
            lbox = self.topo.get_host(self.getMidLeftName(i))
            rbox = self.topo.get_host(self.getMidRightName(i))
            lif = self.getMidL2RInterface(i)
            rif = self.getMidR2LInterface(i)
            logging.info("Put netem command on link {} {}".format(lif, rif))
            cmd = l.build_bandwidth_cmd(lif)
            logging.info(cmd)
            self.topo.command_to(lbox, cmd)
            cmd = l.build_bandwidth_cmd(rif)
            logging.info(cmd)
            self.topo.command_to(rbox, cmd)
            ilif = self.getMidL2RIncomingInterface(i)
            irif = self.getMidR2LIncomingInterface(i)
            cmd = l.build_policing_cmd(ilif)
            logging.info(cmd)
            self.topo.command_to(lbox, cmd)
            cmd = l.build_policing_cmd(irif)
            logging.info(cmd)
            self.topo.command_to(rbox, cmd)
            cmd = l.build_netem_cmd(irif)
            logging.info(cmd)
            self.topo.command_to(rbox, cmd)
            cmd = l.build_netem_cmd(ilif)
            logging.info(cmd)
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

    def configure_interfaces(self):
        """
        Function to override to configure the interfaces of the topology
        """
        pass

    def configure_routing(self):
        """
        Function to override to configure the routing of the topology
        """
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

    def interface_backup_command(self, interface_name):
        return "ip link set dev {} multipath backup ".format(
            interface_name)

    def interface_up_command(self, interface_name, ip, subnet):
        return "ifconfig {} {} netmask {}".format(interface_name, ip, subnet)

    def add_table_route_command(self, from_ip, id):
        return "ip rule add from {} table {}".format(from_ip, id + 1)

    def add_link_scope_route_command(self, network, interface_name, id):
        return "ip route add {} dev {} scope link table {}".format(
            network, interface_name, id + 1)

    def add_table_default_route_command(self, via, id):
        return "ip route add default via {} table {}".format(via, id + 1)

    def add_global_default_route_command(self, via, interface_name):
        return "ip route add default scope global nexthop via {} dev {}".format(via, interface_name)

    def arp_command(self, ip, mac):
        return "arp -s {} {}".format(ip, mac)

    def add_simple_default_route_command(self, via):
        return "ip route add default via {}".format(via)
