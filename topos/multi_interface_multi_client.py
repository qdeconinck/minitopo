from core.topo import Topo, TopoConfig, TopoParameter
import logging


class MultiInterfaceMultiClientTopo(Topo):
    NAME = "MultiIfMultiClient"

    def __init__(self, topo_builder, parameterFile):
        logging.info("Initializing MultiInterfaceTopo...")
        super(MultiInterfaceMultiClientTopo, self).__init__(topo_builder, parameterFile)
        self.router = self.add_router()
        self.c2r_client_switches = []
        self.c2r_router_switches = []

        # First add the base client and server
        self.client = self.add_client()
        self.server = self.add_server()

        # For each client-router, add a client, a bottleneck link, and a server
        for l in self.get_client_to_router_links():
            client = self.add_client()
            server = self.add_server()
            self.c2r_client_switches.append(self.add_c2r_client_side_switch(l))
            self.add_link(self.client, self.c2r_client_switches[-1])
            self.add_link(client, self.c2r_client_switches[-1])
            self.c2r_router_switches.append(self.add_c2r_router_side_switch(l))
            self.add_bottleneck_link(self.c2r_client_switches[-1], self.c2r_router_switches[-1], link_characteristics=l)
            self.add_link(self.c2r_router_switches[-1], self.router)

        # And connect the router to all servers
        for s in self.servers:
            self.add_link(self.router, s)

    def get_client_to_router_links(self):
        return [l for l in self.topo_parameter.link_characteristics if l.link_type == "c2r"]

    def add_c2r_client_side_switch(self, link):
        return self.add_switch("{}c2r{}".format(MultiInterfaceMultiClientTopo.SWITCH_NAME_PREFIX, 2 * link.id))

    def add_c2r_router_side_switch(self, link):
        return self.add_switch("{}c2r{}".format(MultiInterfaceMultiClientTopo.SWITCH_NAME_PREFIX, 2 * link.id + 1))

    def __str__(self):
        s = "Multiple interface topology with several clients and servers\n"
        i = 0
        nc = len(self.get_client_to_router_links())
        for i in range(0, nc):
            if i == nc // 2:
                s = s + "c-               r--s\n"
                s = s + "c-\sw---bl---sw-/ \-s\n"
            else:
                s = s + "c-/sw---bl---sw-\ /-s\n"
        
        return s


class MultiInterfaceMultiClientConfig(TopoConfig):
    NAME = "MultiIfMultiClient"

    def __init__(self, topo, param):
        super(MultiInterfaceMultiClientConfig, self).__init__(topo, param)

    def configure_routing(self):
        for i, l in enumerate(self.topo.c2r_client_switches):
            # Routing for the core client
            cmd = self.add_table_route_command(self.get_client_ip(i), i)
            self.topo.command_to(self.client, cmd)

            cmd = self.add_link_scope_route_command(
                    self.get_client_subnet(i),
                    self.get_client_interface(0, i), i)
            self.topo.command_to(self.client, cmd)

            cmd = self.add_table_default_route_command(self.get_router_ip_to_client_switch(i),
                    i)
            self.topo.command_to(self.client, cmd)

            # Routing for the congestion client
            cmd = self.add_global_default_route_command(self.get_router_ip_to_client_switch(i),
                self.get_client_interface(i+1, 0))
            self.topo.command_to(self.clients[i+1], cmd)

        cmd = self.add_global_default_route_command(self.get_router_ip_to_client_switch(0),
                self.get_client_interface(0, 0))
        self.topo.command_to(self.client, cmd)

        for i, s in enumerate(self.topo.servers):
            cmd = self.add_simple_default_route_command(self.get_router_ip_to_server_switch(i))
            self.topo.command_to(s, cmd)

    def configure_interfaces(self):
        logging.info("Configure interfaces using MultiInterfaceMultiClientConfig...")
        super(MultiInterfaceMultiClientConfig, self).configure_interfaces()
        self.clients = [self.topo.get_client(i) for i in range(0, self.topo.client_count())]
        self.servers = [self.topo.get_server(i) for i in range(0, self.topo.server_count())]
        self.client = self.clients[0]
        self.server = self.servers[0]
        self.router = self.topo.get_router(0)
        netmask = "255.255.255.0"

        for i, l in enumerate(self.topo.c2r_client_switches):
            # Core client
            cmd = self.interface_up_command(self.get_client_interface(0, i), self.get_client_ip(i), netmask)
            self.topo.command_to(self.client, cmd)
            client_interface_mac = self.client.intf(self.get_client_interface(0, i)).MAC()
            self.topo.command_to(self.router, "arp -s {} {}".format(self.get_client_ip(i), client_interface_mac))

            if self.topo.get_client_to_router_links()[i].backup:
                cmd = self.interface_backup_command(self.get_client_interface(0, i))
                self.topo.command_to(self.client, cmd)

            # Congestion client
            cmd = self.interface_up_command(self.get_client_interface(i + 1, 0), self.get_client_ip(i, congestion_client=True), netmask)
            self.topo.command_to(self.clients[i+1], cmd)
            client_interface_mac = self.clients[i+1].intf(self.get_client_interface(i + 1, 0)).MAC()
            self.topo.command_to(self.router, "arp -s {} {}".format(self.get_client_ip(i, congestion_client=True), client_interface_mac))

        for i, l in enumerate(self.topo.c2r_router_switches):
            cmd = self.interface_up_command(self.get_router_interface_to_client_switch(i),
                    self.get_router_ip_to_client_switch(i), netmask)
            self.topo.command_to(self.router, cmd)

            router_interface_mac = self.router.intf(self.get_router_interface_to_client_switch(i)).MAC()
            # Core client
            self.topo.command_to(self.client, "arp -s {} {}".format(
                self.get_router_ip_to_client_switch(i), router_interface_mac))
            # Congestion client
            self.topo.command_to(self.clients[i+1], "arp -s {} {}".format(
                self.get_router_ip_to_client_switch(i), router_interface_mac))

        for i, s in enumerate(self.servers):
            cmd = self.interface_up_command(self.get_router_interface_to_server_switch(i),
                self.get_router_ip_to_server_switch(i), netmask)
            self.topo.command_to(self.router, cmd)
            router_interface_mac = self.router.intf(self.get_router_interface_to_server_switch(i)).MAC()
            self.topo.command_to(s, "arp -s {} {}".format(
                self.get_router_ip_to_server_switch(i), router_interface_mac))
            cmd = self.interface_up_command(self.get_server_interface(i, 0), self.get_server_ip(interface_index=i), netmask)
            self.topo.command_to(s, cmd)
            server_interface_mac = s.intf(self.get_server_interface(i, 0)).MAC()
            self.topo.command_to(self.router, "arp -s {} {}".format(
                self.get_server_ip(interface_index=i), server_interface_mac))

    def get_client_ip(self, interface_index, congestion_client=False):
        return "{}{}.{}".format(self.param.get(TopoParameter.LEFT_SUBNET), interface_index, "10" if congestion_client else "1")

    def get_client_subnet(self, interface_index):
        return "{}{}.0/24".format(self.param.get(TopoParameter.LEFT_SUBNET), interface_index)

    def get_router_ip_to_client_switch(self, switch_index):
        return "{}{}.2".format(self.param.get(TopoParameter.LEFT_SUBNET), switch_index)

    def get_router_ip_to_server_switch(self, switch_index):
        return "{}{}.2".format(self.param.get(TopoParameter.RIGHT_SUBNET), switch_index)

    def get_server_ip(self, interface_index=0):
        return "{}{}.1".format(self.param.get(TopoParameter.RIGHT_SUBNET), interface_index)

    def get_server_subnet(self, interface_index):
        return "{}{}.0/24".format(self.param.get(TopoParameter.RIGHT_SUBNET), interface_index)

    def client_interface_count(self):
        return max(len(self.topo.c2r_client_switches), 1)

    def server_interface_count(self):   
        return max(len(self.servers), 1)

    def get_router_interface_to_server_switch(self, switch_index):
        return self.get_router_interface_to_client_switch(len(self.topo.c2r_router_switches) + switch_index)

    def get_client_interface(self, client_index, interface_index):
        return "{}-eth{}".format(self.topo.get_client_name(client_index), interface_index)

    def get_router_interface_to_client_switch(self, interface_index):
        return "{}-eth{}".format(self.topo.get_router_name(0), interface_index)

    def get_server_interface(self, server_index, interface_index):
        return "{}-eth{}".format(self.topo.get_server_name(server_index), interface_index)