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


def get_bandwidth_delay_product_divided_by_mtu(delay, bandwidth):
    """
    With delay in ms, bandwidth in Mbps
    """
    rtt = 2 * float(delay)
    bandwidth_delay_product = (float(bandwidth) * 125000.0) * (rtt / 1000.0)
    return int(math.ceil(bandwidth_delay_product * 1.0 / 1500.0))


class LinkCharacteristics(object):
    """
    Network characteristics associated to a link

    Attributes:
        id              the identifier of the link
        link_type       type of the link
        delay           the one-way delay introduced by the link in ms
        queue_size      the size of the link buffer, in packets
        bandwidth       the bandwidth of the link in Mbps
        loss            the random loss rate in percentage
        queuing_delay   the maximum time that a packet can stay in the link buffer (computed over queue_size)
        netem_at        list of NetemAt instances applicable to the link
        backup          integer indicating if this link is a backup one or not (useful for MPTCP)
    """
    def __init__(self, id, link_type, delay, queue_size, bandwidth, loss, backup=0):
        self.id = id
        self.link_type = link_type
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
        return get_bandwidth_delay_product_divided_by_mtu(self.delay, self.bandwidth)

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

    def build_delete_tc_cmd(self, ifname):
        return "tc qdisc del dev {} root; tc qdisc del dev {} ingress ".format(ifname, ifname)

    def build_bandwidth_cmd(self, ifname, change=False):
        return "tc qdisc {} dev {} root handle 5:0 tbf rate {}mbit burst 15000 limit {}".format(
            "change" if change else "add", ifname, self.bandwidth, self.buffer_size())

    def build_changing_bandwidth_cmd(self, ifname):
        return "&& ".join(
            ["sleep {} && {} ".format(
                n.delta, self.build_bandwidth_cmd(ifname, change=True)) for n in self.netem_at]
            + ["true &"]
        )

    def build_netem_cmd(self, ifname, cmd, change=False):
        return "tc qdisc {} dev {} root handle 10: netem {} {}".format(
            "change" if change else "add", ifname, cmd, "delay {}ms limit 50000".format(self.delay) if not change else "")

    def build_changing_netem_cmd(self, ifname):
        return "&& ".join(
            ["sleep {} && {} ".format(
                n.delta, self.build_netem_cmd(ifname, n.cmd, change=True)) for n in self.netem_at]
            + ["true &"]
        )

    def build_policing_cmd(self, ifname, change=False):
        return "tc qdisc {} dev {} handle ffff: ingress ; \
            tc filter {} dev {} parent ffff: u32 match u32 0 0 police rate {}mbit burst {} drop".format(
                "change" if change else "add", ifname, "change" if change else "add", ifname,
                self.bandwidth, int(self.buffer_size()) * 1.2)

    def build_changing_policing_cmd(self, ifname):
        return "&& ".join(
            ["sleep {} && {} ".format(
                n.delta, self.build_policing_cmd(ifname, change=True)) for n in self.netem_at]
            + ["true &"]
        )

    def as_dict(self):
        """
        Notably used by BottleneckLink
        """
        return {
            "link_id": self.id,
            "link_type": self.link_type,
            "bw": float(self.bandwidth),
            "delay": "{}ms".format(self.delay),
            "loss": float(self.loss),
            "max_queue_size": int(self.queue_size)
        }

    def __str__(self):
        return """
Link type: {}
Link id: {}
    Delay: {}
    Queue Size: {}
    Bandwidth: {}
    Loss: {}
    Backup: {}
        """.format(self.link_type, self.id, self.delay, self.queue_size, self.bandwidth, self.loss, self.backup) + \
            "".join(["\t {} \n".format(n) for n in self.netem_at])


class TopoParameter(Parameter):
    LEFT_SUBNET = "leftSubnet"
    RIGHT_SUBNET = "rightSubnet"
    NETEM_AT = "netemAt_"
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

    def parse_netem_at(self, key):
        """
        Parse key of the form netemAt_{link_type}_{link_id}

        Return link_type, link_id
        """
        _, link_type, link_id = key.split("_")
        return link_type, int(link_id)

    def load_netem_at(self):
        if not self.get(TopoParameter.CHANGE_NETEM) == "yes":
            return
        for k in sorted(self.parameters):
            if k.startswith(TopoParameter.NETEM_AT):
                link_type, link_id = self.parse_netem_at(k)
                self.load_netem_at_value(link_type, link_id, self.parameters[k])

    def find_link_characteristic(self, link_type, link_id):
        for l in self.link_characteristics:
            if l.link_type == link_type and l.id == link_id:
                return l

        return ValueError("No link with link_type {} and link_id {}".format(link_type, link_id))

    def load_netem_at_value(self, link_type, link_id, n):
        try:
            at, cmd = n.split(",")
            na = NetemAt(float(at), cmd)
            l = self.find_link_characteristic(link_type, link_id)
            l.add_netem_at(na)

        except ValueError as e:
            logging.error("Unable to set netem for link {} with command {}: {}".format(link_id, n, e))

        logging.info(self.link_characteristics[link_id].netem_at)

    def parse_link_id_and_type(self, key):
        """
        The key of a path must have the following format:
            path_{link_type}_{ID}

        Note that several links can have the same ID, several links can have the same
        link_type, but the tuple (link_type, ID) is unique.
        """
        _, link_type, link_id = key.split("_")
        return link_type, int(link_id)

    def parse_link_characteristics(self, value):
        """
        The format of a link characteristic is one of the following:
            - "{delay},{queue_size},{bandwidth},{loss_perc},{is_backup}"
            - "{delay},{queue_size},{bandwidth},{loss_perc}"
            - "{delay},{queue_size},{bandwidth}"
            - "{delay},{bandwidth}"

        When not specified, default values are the following:
            - queue_size: get_bandwidth_delay_product_divided_by_mtu(delay, bandwidth)
            - loss_perc: 0
            - is_backup: 0

        Return
            delay, bandwidth, queue_size, loss_perc, is_backup
        """
        loss_perc, is_backup = 0.0, 0
        c = value.split(",")
        if len(c) == 2:
            delay, bw = float(c[0]), float(c[1])
            return delay, bw, get_bandwidth_delay_product_divided_by_mtu(delay, bw), loss_perc, is_backup
        if len(c) == 3:
            return float(c[0]), float(c[2]), int(c[1]), loss_perc, is_backup
        if len(c) == 4:
            return float(c[0]), float(c[2]), int(c[1]), float(c[3]), is_backup
        if len(c) == 5:
            return float(c[0]), float(c[2]), int(c[1]), float(c[3]), int(c[4])

        raise ValueError("Invalid link characteristics: {}".format(value))

    def load_link_characteristics(self):
        """
        Load the path characteristics
        """
        for k in sorted(self.parameters):
            if k.startswith("path"):
                try:
                    link_type, link_id = self.parse_link_id_and_type(k)
                    delay, bw, queue_size, loss_perc, is_backup = self.parse_link_characteristics(
                        self.parameters[k])
                except ValueError as e:
                    logging.error("Ignored path {}: {}".format(k, e))
                else:
                    path = LinkCharacteristics(link_id, link_type, delay, queue_size,
                            bw, loss_perc, backup=is_backup)
                    self.link_characteristics.append(path)

    def __str__(self):
        s = "{}".format(super(TopoParameter, self).__str__())
        s += "".join(["{}".format(lc) for lc in self.link_characteristics])
        return s


class BottleneckLink(object):
    """
    Representation of a bottleneck link having limited bandwidth, a buffer,
    experiencing propagation delay and introducing packet losses.

    A bottleneck link has the following actual representation:

        bs0 -- bs1 -- bs2 -- bs3

    Where bs0 (resp. bs3) is the left (resp. right) side of the link, and having
    TC commands for the packet flow s0 -> s3 as follows:
        - Policing command to implement buffer on ingress of bs1 from bs0
        - Shaping command to implement bandwidth on egress of bs1 to bs2
        - Netem command to implement delay and loss on egress of bs2 to bs3
    """
    BOTTLENECK_SWITCH_NAME_PREFIX = "bs"

    def __init__(self, topo_builder, topo, link_characteristics):
        self.link_characteristics = link_characteristics
        self.topo = topo
        self.bs0 = topo_builder.add_switch(self.get_bs_name(0))
        self.bs1 = topo_builder.add_switch(self.get_bs_name(1))
        self.bs2 = topo_builder.add_switch(self.get_bs_name(2))
        self.bs3 = topo_builder.add_switch(self.get_bs_name(3))
        topo_builder.add_link(self.bs0, self.bs1)
        topo_builder.add_link(self.bs1, self.bs2)
        topo_builder.add_link(self.bs2, self.bs3)

    def get_bs_name(self, index):
        return "{}_{}_{}_{}".format(BottleneckLink.BOTTLENECK_SWITCH_NAME_PREFIX, 
            self.link_characteristics.link_type, self.link_characteristics.id, index)

    def reinit_variables(self):
        # Required to retrieve actual nodes
        self.bs0 = self.topo.get_host(self.get_bs_name(0))
        self.bs1 = self.topo.get_host(self.get_bs_name(1))
        self.bs2 = self.topo.get_host(self.get_bs_name(2))
        self.bs3 = self.topo.get_host(self.get_bs_name(3))

    def configure_bottleneck(self):
        bs1_interface_names = self.topo.get_interface_names(self.bs1)
        bs2_interface_names = self.topo.get_interface_names(self.bs2)

        # Cleanup tc commands
        for bs1_ifname in bs1_interface_names:
            clean_cmd = self.link_characteristics.build_delete_tc_cmd(bs1_ifname)
            logging.info(clean_cmd)
            self.topo.command_to(self.bs1, clean_cmd)

        for bs2_ifname in bs2_interface_names:
            clean_cmd = self.link_characteristics.build_delete_tc_cmd(bs2_ifname)
            logging.info(clean_cmd)
            self.topo.command_to(self.bs2, clean_cmd)

        # Flow bs0 -> bs3
        policing_cmd = self.link_characteristics.build_policing_cmd(bs1_interface_names[0])
        logging.info(policing_cmd)
        self.topo.command_to(self.bs1, policing_cmd)
        shaping_cmd = self.link_characteristics.build_bandwidth_cmd(bs1_interface_names[-1])
        logging.info(shaping_cmd)
        self.topo.command_to(self.bs1, shaping_cmd)
        netem_cmd = self.link_characteristics.build_netem_cmd(bs2_interface_names[-1],
            "loss {}".format(self.link_characteristics.loss) if float(self.link_characteristics.loss) > 0 else "")
        logging.info(netem_cmd)
        self.topo.command_to(self.bs2, netem_cmd)

        # Flow bs3 -> bs0
        policing_cmd = self.link_characteristics.build_policing_cmd(bs2_interface_names[-1])
        logging.info(policing_cmd)
        self.topo.command_to(self.bs2, policing_cmd)
        shaping_cmd = self.link_characteristics.build_bandwidth_cmd(bs2_interface_names[0])
        logging.info(shaping_cmd)
        self.topo.command_to(self.bs2, shaping_cmd)
        netem_cmd = self.link_characteristics.build_netem_cmd(bs1_interface_names[0],
            "loss {}".format(self.link_characteristics.loss) if float(self.link_characteristics.loss) > 0 else "")
        logging.info(netem_cmd)
        self.topo.command_to(self.bs1, netem_cmd)

    def configure_changing_bottleneck(self):
        bs1_interface_names = self.topo.get_interface_names(self.bs1)
        bs2_interface_names = self.topo.get_interface_names(self.bs2)
        # Flow bs0 -> bs3
        policing_cmd = self.link_characteristics.build_changing_policing_cmd(bs1_interface_names[0])
        logging.info(policing_cmd)
        self.topo.command_to(self.bs1, policing_cmd)
        shaping_cmd = self.link_characteristics.build_changing_bandwidth_cmd(bs1_interface_names[-1])
        logging.info(shaping_cmd)
        self.topo.command_to(self.bs1, shaping_cmd)
        netem_cmd = self.link_characteristics.build_changing_netem_cmd(bs2_interface_names[-1])
        logging.info(netem_cmd)
        self.topo.command_to(self.bs2, netem_cmd)

        # Flow bs3 -> bs0
        policing_cmd = self.link_characteristics.build_changing_policing_cmd(bs2_interface_names[-1])
        logging.info(policing_cmd)
        self.topo.command_to(self.bs2, policing_cmd)
        shaping_cmd = self.link_characteristics.build_changing_bandwidth_cmd(bs2_interface_names[0])
        logging.info(shaping_cmd)
        self.topo.command_to(self.bs2, shaping_cmd)
        netem_cmd = self.link_characteristics.build_changing_netem_cmd(bs1_interface_names[0])
        logging.info(netem_cmd)
        self.topo.command_to(self.bs1, netem_cmd)

    def get_left(self):
        return self.bs0

    def get_right(self):
        return self.bs3


class Topo(object):
    """
    Base class to instantiate a topology.

    The network topology has always the following elements:
        - a (set of) client(s)
        - a (set of) router(s)
        - a (set of) server(s)
        - a set of bottleneck links

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
    CLIENT_NAME_PREFIX = "Client"
    SERVER_NAME_PREFIX = "Server"
    ROUTER_NAME_PREFIX = "Router"
    CMD_LOG_FILENAME = "command.log"

    def __init__(self, topo_builder, topo_parameter):
        self.topo_builder = topo_builder
        self.topo_parameter = topo_parameter
        self.change_netem = topo_parameter.get(TopoParameter.CHANGE_NETEM).lower() == "yes"
        self.log_file = open(Topo.CMD_LOG_FILENAME, 'w')
        self.clients = []
        self.routers = []
        self.servers = []
        self.bottleneck_links = []

    def get_client_name(self, index):
        return "{}_{}".format(Topo.CLIENT_NAME_PREFIX, index)

    def get_router_name(self, index):
        return "{}_{}".format(Topo.ROUTER_NAME_PREFIX, index)

    def get_server_name(self, index):
        return "{}_{}".format(Topo.SERVER_NAME_PREFIX, index)

    def add_client(self):
        client = self.add_host(self.get_client_name(self.client_count()))
        self.clients.append(client)
        return client

    def add_router(self):
        router = self.add_host(self.get_router_name(self.router_count()))
        self.routers.append(router)
        return router

    def add_server(self):
        server = self.add_host(self.get_server_name(self.server_count()))
        self.servers.append(server)
        return server

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

    def client_count(self):
        return len(self.clients)

    def get_client(self, index):
        return self.clients[index]

    def get_router(self, index):
        return self.routers[index]

    def get_server(self, index):
        return self.servers[index]

    def router_count(self):
        return len(self.routers)

    def server_count(self):
        return len(self.servers)

    def bottleneck_link_count(self):
        return len(self.bottleneck_links)

    def get_host(self, who):
        return self.topo_builder.get_host(who)

    def get_interface_names(self, who):
        return self.topo_builder.get_interface_names(who)

    def add_host(self, host):
        return self.topo_builder.add_host(host)

    def add_switch(self, switch):
        return self.topo_builder.add_switch(switch)

    def add_link(self, from_a, to_b, **kwargs):
        self.topo_builder.add_link(from_a, to_b, **kwargs)

    def add_bottleneck_link(self, from_a, to_b, link_characteristics=None, bottleneck_link=None):
        """
        If bottleneck_link is None, create a bottleneck link with parameters kwargs,
        otherwise just connect it to from_a and to_b and returns the bottleneck_link
        """
        if bottleneck_link is None:
            bottleneck_link = BottleneckLink(self.topo_builder, self, link_characteristics)
            self.bottleneck_links.append(bottleneck_link)

        self.topo_builder.add_link(from_a, bottleneck_link.get_left())
        self.topo_builder.add_link(bottleneck_link.get_right(), to_b)
        return bottleneck_link

    def reinit_variables(self):
        # Because we create nodes before starting mininet
        self.clients = [self.get_host(self.get_client_name(i)) for i in range(len(self.clients))]
        self.routers = [self.get_host(self.get_router_name(i)) for i in range(len(self.routers))]
        self.servers = [self.get_host(self.get_server_name(i)) for i in range(len(self.servers))]
        for b in self.bottleneck_links:
            b.reinit_variables()

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
        self.topo.reinit_variables()
        self.disable_tso()
        logging.debug("Configure network in TopoConfig")
        self.configure_interfaces()
        self.configure_routing()

    def disable_tso(self):
        """
        Disable TSO on all interfaces
        """
        for node in [self.topo.get_host(n) for n in self.topo.topo_builder.net]:
            for intf in self.topo.get_interface_names(node):
                logging.info("Disable TSO on interface {}".format(intf))
                cmd = "ethtool -K {} tso off".format(intf)
                logging.info(cmd)
                self.topo.command_to(node, cmd)

    def run_netem_at(self):
        """
        Prepare netem commands to be run after some delay
        """
        if not self.topo.change_netem:
            # Just rely on defaults of TCLink
            logging.info("No need to change netem")
            return

        logging.info("Will change netem config on the fly")
        for b in self.topo.bottleneck_links:
            b.configure_changing_bottleneck()

    def configure_interfaces(self):
        """
        Function to inherit to configure the interfaces of the topology
        """
        for b in self.topo.bottleneck_links:
            b.configure_bottleneck()

    def configure_routing(self):
        """
        Function to override to configure the routing of the topology
        """
        pass

    def client_interface_count(self):
        """
        Return the number of client's interfaces, without lo
        """
        raise NotImplementedError()

    def server_interface_count(self):
        """
        Return the number of server's interfaces, without lo
        """
        raise NotImplementedError()

    def get_client_interface(self, client_index, interface_index):
        """
        Return the interface with index `interface_index` of the client with index `client_index` 
        """
        raise NotImplementedError()

    def get_server_interface(self, server_index, interface_index):
        """
        Return the interface with index `interface_index` of the server with index `server_index` 
        """
        raise NotImplementedError()

    def get_router_interface_to_client_switch(self, index):
        """
        Return the router's interface to client's switch with index `index`
        """
        raise NotImplementedError()

    def get_router_interface_to_server_switch(self, index):
        """
        Return the router's interface to server's switch with index `index`
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
