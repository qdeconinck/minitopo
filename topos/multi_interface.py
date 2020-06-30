from core.topo import Topo, TopoConfig, TopoParameter
import logging


class MultiInterfaceTopo(Topo):
    NAME = "MultiIf"

    def __init__(self, topo_builder, parameterFile):
        logging.info("Initializing MultiInterfaceTopo...")
        super(MultiInterfaceTopo, self).__init__(topo_builder, parameterFile)
        self.client = self.add_client()
        self.server = self.add_server()
        self.router = self.add_router()
        self.client_switches = []
        self.server_switches = []
        for l in self.topo_parameter.link_characteristics:
            self.client_switches.append(self.add_client_side_switch(l))
            self.add_link(self.client,self.client_switches[-1])
            self.server_switches.append(self.add_router_side_switch(l))
            self.add_bottleneck_link(self.client_switches[-1], self.server_switches[-1], link_characteristics=l)
            self.add_link(self.server_switches[-1],self.router)
        self.add_link(self.router, self.server)

    def add_client_side_switch(self, link):
        return self.add_switch("{}{}".format(MultiInterfaceTopo.SWITCH_NAME_PREFIX, 2 * link.id))

    def add_router_side_switch(self, link):
        return self.add_switch("{}{}".format(MultiInterfaceTopo.SWITCH_NAME_PREFIX, 2 * link.id + 1))

    def __str__(self):
        s = "Simple multiple interface topolgy \n"
        i = 0
        n = len(self.topo_parameter.link_characteristics)
        for p in self.topo_parameter.link_characteristics:
            if i == n // 2:
                if n % 2 == 0:
                    s = s + "c            r-----s\n"
                    s = s + "|--sw----sw--|\n"
                else:
                    s = s + "c--sw----sw--r-----s\n"
            else:
                s = s + "|--sw----sw--|\n"

            i = i + 1
        return s

class MultiInterfaceConfig(TopoConfig):
    NAME = "MultiIf"

    def __init__(self, topo, param):
        super(MultiInterfaceConfig, self).__init__(topo, param)

    def configure_routing(self):
        for i, l in enumerate(self.topo.client_switches):
            cmd = self.add_table_route_command(self.get_client_ip(i), i)
            self.topo.command_to(self.client, cmd)

            cmd = self.add_link_scope_route_command(
                    self.get_client_subnet(i),
                    self.get_client_interface(0, i), i)
            self.topo.command_to(self.client, cmd)

            cmd = self.add_table_default_route_command(self.get_router_ip_to_switch(i),
                    i)
            self.topo.command_to(self.client, cmd)

        cmd = self.add_global_default_route_command(self.get_router_ip_to_switch(0),
                self.get_client_interface(0, 0))
        self.topo.command_to(self.client, cmd)

        cmd = self.add_simple_default_route_command(self.get_router_ip_to_server())
        self.topo.command_to(self.server, cmd)


    def configure_interfaces(self):
        logging.info("Configure interfaces using MultiInterfaceConfig...")
        super(MultiInterfaceConfig, self).configure_interfaces()
        self.client = self.topo.get_client(0)
        self.server = self.topo.get_server(0)
        self.router = self.topo.get_router(0)
        netmask = "255.255.255.0"

        links = self.topo.get_link_characteristics()
        for i, l in enumerate(self.topo.client_switches):
            cmd = self.interface_up_command(self.get_client_interface(0, i), self.get_client_ip(i), netmask)
            self.topo.command_to(self.client, cmd)
            client_interface_mac = self.client.intf(self.get_client_interface(0, i)).MAC()
            self.topo.command_to(self.router, "arp -s {} {}".format(self.get_client_ip(i), client_interface_mac))

            if(links[i].backup):
                cmd = self.interface_backup_command(self.get_client_interface(0, i))
                self.topo.command_to(self.client, cmd)

        for i, l in enumerate(self.topo.server_switches):
            cmd = self.interface_up_command(self.get_router_interface_to_switch(i),
                    self.get_router_ip_to_switch(i), netmask)
            self.topo.command_to(self.router, cmd)
            router_interface_mac = self.router.intf(self.get_router_interface_to_switch(i)).MAC()
            self.topo.command_to(self.client, "arp -s {} {}".format(
                self.get_router_ip_to_switch(i), router_interface_mac))

        cmd = self.interface_up_command(self.get_router_interface_to_server(),
                self.get_router_ip_to_server(), netmask)
        self.topo.command_to(self.router, cmd)
        router_interface_mac = self.router.intf(self.get_router_interface_to_server()).MAC()
        self.topo.command_to(self.server, "arp -s {} {}".format(
            self.get_router_ip_to_server(), router_interface_mac))

        cmd = self.interface_up_command(self.get_server_interface(0), self.get_server_ip(), netmask)
        self.topo.command_to(self.server, cmd)
        server_interface_mac = self.server.intf(self.get_server_interface(0)).MAC()
        self.topo.command_to(self.router, "arp -s {} {}".format(
            self.get_server_ip(), server_interface_mac))

    def get_client_ip(self, interface_index):
        return "{}{}.1".format(self.param.get(TopoParameter.LEFT_SUBNET), interface_index)

    def get_client_subnet(self, interface_index):
        return "{}{}.0/24".format(self.param.get(TopoParameter.LEFT_SUBNET), interface_index)

    def get_router_ip_to_switch(self, switch_index):
        return "{}{}.2".format(self.param.get(TopoParameter.LEFT_SUBNET), switch_index)

    def get_router_ip_to_server(self):
        return "{}0.2".format(self.param.get(TopoParameter.RIGHT_SUBNET))

    def get_server_ip(self):
        return "{}0.1".format(self.param.get(TopoParameter.RIGHT_SUBNET))

    def client_interface_count(self):
        return len(self.topo.client_switches)

    def get_router_interface_to_server(self):
        return self.get_router_interface_to_switch(len(self.topo.server_switches))

    def get_client_interface(self, client_index, interface_index):
        return "{}-eth{}".format(self.topo.get_client_name(client_index), interface_index)

    def get_router_interface_to_switch(self, interface_index):
        return "{}-eth{}".format(self.topo.get_router_name(0), interface_index)

    def get_server_interface(self, server_index):
        return "{}-eth0".format(self.topo.get_server_name(server_index))