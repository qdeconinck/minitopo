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
        self.c2r_links = []
        self.r2s_links = []

        # Add client - router links
        for l in self.get_client_to_router_links():
            self.c2r_links.append(self.add_bottleneck_link(self.client, self.router, link_characteristics=l))

        # Special case: if there is no specified link between router and server, directly connect them!
        if len(self.get_router_to_server_links()) > 0:
            for l in self.get_router_to_server_links():
                self.r2s_links.append(self.add_bottleneck_link(self.router, self.server, link_characteristics=l))
        else:
            self.add_link(self.router, self.server)
            

    def get_client_to_router_links(self):
        return [l for l in self.topo_parameter.link_characteristics if l.link_type == "c2r"]

    def get_router_to_server_links(self):
        return [l for l in self.topo_parameter.link_characteristics if l.link_type == "r2s"]

    def __str__(self):
        s = "Simple multiple interface topology \n"
        i = 0
        nc = len(self.get_client_to_router_links())
        ns = len(self.get_router_to_server_links())
        m = max(nc, ns)
        skipped = 0
        for i in range(0, m):
            if i == m // 2:
                if m % 2 == 0:
                    s = s + "c                r                s\n"
                    s = s + " \-sw---bl---sw-/ \-sw---bl---sw-/\n"
                else:
                    s = s + "c--sw---bl---sw--r--sw---bl---sw--s\n"
            else:
                if i < m // 2:
                    if (nc == m and ns + skipped == m) or (ns == m and nc + skipped == m):
                        s = s + " /-sw---bl---sw-\ /-sw---bl---sw-\ \n"
                    elif nc == m:
                        s = s + " /-sw---bl---sw-\ \n"
                        skipped += 1
                    else:
                        s = s + "                  /-sw---bl---sw-\ \n"
                        skipped += 1
                else:
                    if (nc == m and ns + skipped == m) or (ns == m and nc + skipped == m):
                        s = s + " \-sw---bl---sw-/ \-sw---bl---sw-/ \n"
                    elif nc == m:
                        s = s + " \-sw---bl---sw-/ \n"
                        skipped += 1
                    else:
                        s = s + "                  \-sw---bl---sw-/ \n"
                        skipped += 1
        
        return s


class MultiInterfaceConfig(TopoConfig):
    NAME = "MultiIf"

    def __init__(self, topo, param):
        super(MultiInterfaceConfig, self).__init__(topo, param)

    def configure_routing(self):
        for i, _ in enumerate(self.topo.c2r_links):
            cmd = self.add_table_route_command(self.get_client_ip(i), i)
            self.topo.command_to(self.client, cmd)

            cmd = self.add_link_scope_route_command(
                    self.get_client_subnet(i),
                    self.get_client_interface(0, i), i)
            self.topo.command_to(self.client, cmd)

            cmd = self.add_table_default_route_command(self.get_router_ip_to_client_switch(i),
                    i)
            self.topo.command_to(self.client, cmd)

        for i, _ in enumerate(self.topo.r2s_links):
            cmd = self.add_table_route_command(self.get_server_ip(i), i)
            self.topo.command_to(self.server, cmd)

            cmd = self.add_link_scope_route_command(
                    self.get_server_subnet(i),
                    self.get_server_interface(0, i), i)
            self.topo.command_to(self.server, cmd)

            cmd = self.add_table_default_route_command(self.get_router_ip_to_server_switch(i),
                    i)
            self.topo.command_to(self.server, cmd)

        cmd = self.add_global_default_route_command(self.get_router_ip_to_client_switch(0),
                self.get_client_interface(0, 0))
        self.topo.command_to(self.client, cmd)

        cmd = self.add_simple_default_route_command(self.get_router_ip_to_server_switch(0))
        self.topo.command_to(self.server, cmd)


    def configure_interfaces(self):
        logging.info("Configure interfaces using MultiInterfaceConfig...")
        super(MultiInterfaceConfig, self).configure_interfaces()
        self.client = self.topo.get_client(0)
        self.server = self.topo.get_server(0)
        self.router = self.topo.get_router(0)
        netmask = "255.255.255.0"

        for i, _ in enumerate(self.topo.c2r_links):
            cmd = self.interface_up_command(self.get_client_interface(0, i), self.get_client_ip(i), netmask)
            self.topo.command_to(self.client, cmd)
            client_interface_mac = self.client.intf(self.get_client_interface(0, i)).MAC()
            self.topo.command_to(self.router, "arp -s {} {}".format(self.get_client_ip(i), client_interface_mac))

            if self.topo.get_client_to_router_links()[i].backup:
                cmd = self.interface_backup_command(self.get_client_interface(0, i))
                self.topo.command_to(self.client, cmd)

        for i, _ in enumerate(self.topo.c2r_links):
            cmd = self.interface_up_command(self.get_router_interface_to_client_switch(i),
                    self.get_router_ip_to_client_switch(i), netmask)
            self.topo.command_to(self.router, cmd)
            router_interface_mac = self.router.intf(self.get_router_interface_to_client_switch(i)).MAC()
            self.topo.command_to(self.client, "arp -s {} {}".format(
                self.get_router_ip_to_client_switch(i), router_interface_mac))

        if len(self.topo.r2s_links) == 0:
            # Case no server param is specified
            cmd = self.interface_up_command(self.get_router_interface_to_server_switch(0),
                    self.get_router_ip_to_server_switch(0), netmask)
            self.topo.command_to(self.router, cmd)
            router_interface_mac = self.router.intf(self.get_router_interface_to_server_switch(0)).MAC()
            self.topo.command_to(self.server, "arp -s {} {}".format(
                self.get_router_ip_to_server_switch(0), router_interface_mac))

            cmd = self.interface_up_command(self.get_server_interface(0, 0), self.get_server_ip(0), netmask)
            self.topo.command_to(self.server, cmd)
            server_interface_mac = self.server.intf(self.get_server_interface(0, 0)).MAC()
            self.topo.command_to(self.router, "arp -s {} {}".format(
                self.get_server_ip(0), server_interface_mac))

        for i, _ in enumerate(self.topo.r2s_links):
            cmd = self.interface_up_command(self.get_router_interface_to_server_switch(i),
                    self.get_router_ip_to_server_switch(i), netmask)
            self.topo.command_to(self.router, cmd)
            router_interface_mac = self.router.intf(self.get_router_interface_to_server_switch(i)).MAC()
            self.topo.command_to(self.server, "arp -s {} {}".format(
                self.get_router_ip_to_server_switch(i), router_interface_mac))

        for i, _ in enumerate(self.topo.r2s_links):
            cmd = self.interface_up_command(self.get_server_interface(0, i), self.get_server_ip(i), netmask)
            self.topo.command_to(self.server, cmd)
            server_interface_mac = self.server.intf(self.get_server_interface(0, i)).MAC()
            self.topo.command_to(self.router, "arp -s {} {}".format(
                self.get_server_ip(i), server_interface_mac))

    def get_client_ip(self, interface_index):
        return "{}{}.1".format(self.param.get(TopoParameter.LEFT_SUBNET), interface_index)

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
        return max(len(self.topo.c2r_links), 1)

    def server_interface_count(self):
        return max(len(self.topo.r2s_links), 1)

    def get_router_interface_to_server_switch(self, switch_index):
        return self.get_router_interface_to_client_switch(len(self.topo.c2r_links) + switch_index)

    def get_client_interface(self, client_index, interface_index):
        return "{}-eth{}".format(self.topo.get_client_name(client_index), interface_index)

    def get_router_interface_to_client_switch(self, interface_index):
        return "{}-eth{}".format(self.topo.get_router_name(0), interface_index)

    def get_server_interface(self, server_index, interface_index):
        return "{}-eth{}".format(self.topo.get_server_name(server_index), interface_index)