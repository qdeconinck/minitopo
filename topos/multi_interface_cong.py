from core.topo import TopoConfig, Topo, TopoParameter


class MultiInterfaceCongTopo(Topo):
    NAME = "MultiIfCong"

    congClientName = "CCli"
    congServerName = "CSer"

    def __init__(self, topo_builder, parameterFile):
        raise Exception("Broken")
        super(MultiInterfaceCongTopo, self).__init__(topo_builder, parameterFile)
        print("Hello from topo multi if")
        self.client = self.add_host(Topo.CLIENT_NAME)
        self.server = self.add_host(Topo.SERVER_NAME)
        self.router = self.add_host(Topo.ROUTER_NAME)
        self.cong_clients = []
        self.cong_servers = []
        self.switch = []
        for l in self.topo_parameter.link_characteristics:
            self.switch.append(self.addOneSwitchPerLink(l))
            self.add_link(self.client,self.switch[-1])
            self.cong_clients.append(self.add_host(MultiInterfaceCongTopo.congClientName + str(len(self.cong_clients))))
            self.add_link(self.cong_clients[-1], self.switch[-1])
            self.add_link(self.switch[-1],self.router, **l.as_dict())
        self.add_link(self.router, self.server)
        for i in range(len(self.cong_clients)):
            self.cong_servers.append(self.add_host(MultiInterfaceCongTopo.congServerName + str(len(self.cong_servers))))
            self.add_link(self.router, self.cong_servers[-1])

    def getCongClients(self):
        return self.cong_clients

    def getCongServers(self):
        return self.cong_servers

    def addOneSwitchPerLink(self, link):
        return self.add_switch(MultiInterfaceCongTopo.SWITCH_NAME_PREFIX +
                str(link.id))

    def __str__(self):
        s = "Simple multiple interface topology with congestion \n"
        i = 0
        n = len(self.topo_parameter.link_characteristics)
        for p in self.topo_parameter.link_characteristics:
            if i == n // 2:
                if n % 2 == 0:
                    s = s + "c            r-----s\n"
                    s = s + "|-----sw-----|\n"
                else:
                    s = s + "c-----sw-----r-----s\n"
            else:
                s = s + "|-----sw-----|\n"

            i = i + 1
        return s


class MultiInterfaceCongConfig(TopoConfig):
    NAME = "MultiIfCong"

    def __init__(self, topo, param):
        super(MultiInterfaceCongConfig, self).__init__(topo, param)

    def configure_routing(self):
        i = 0
        for l in self.topo.switch:
            cmd = self.add_table_route_command(self.getClientIP(i), i)
            self.topo.command_to(self.client, cmd)

            # Congestion client
            cmd = self.add_table_route_command(self.getCongClientIP(i), i)
            self.topo.command_to(self.cong_clients[i], cmd)

            cmd = self.add_link_scope_route_command(
                    self.getClientSubnet(i),
                    self.get_client_interface(i), i)
            self.topo.command_to(self.client, cmd)

            # Congestion client
            cmd = self.add_link_scope_route_command(
                    self.getClientSubnet(i),
                    self.getCongClientInterface(i), i)
            self.topo.command_to(self.cong_clients[i], cmd)

            cmd = self.add_table_default_route_command(self.getRouterIPSwitch(i),
                    i)
            self.topo.command_to(self.client, cmd)

            # Congestion client
            # Keep the same command
            self.topo.command_to(self.cong_clients[i], cmd)

            # Congestion client
            cmd = self.add_global_default_route_command(self.getRouterIPSwitch(i),
                    self.getCongClientInterface(i))
            i = i + 1

        cmd = self.add_global_default_route_command(self.getRouterIPSwitch(0),
                self.get_client_interface(0))
        self.topo.command_to(self.client, cmd)

        # Congestion Client
        i = 0
        for c in self.cong_clients:
            cmd = self.add_global_default_route_command(self.getRouterIPSwitch(i),
                self.getCongClientInterface(i))
            self.topo.command_to(c, cmd)
            i = i + 1

        cmd = self.add_simple_default_route_command(self.getRouterIPServer())
        self.topo.command_to(self.server, cmd)
        # Congestion servers
        i = 0
        for s in self.cong_servers:
            cmd = self.add_simple_default_route_command(self.getRouterIPCongServer(i))
            self.topo.command_to(s, cmd)
            i += 1


    def configure_interfaces(self):
        print("Configure interfaces for multi inf")
        self.client = self.topo.get_host(Topo.CLIENT_NAME)
        self.server = self.topo.get_host(Topo.SERVER_NAME)
        self.router = self.topo.get_host(Topo.ROUTER_NAME)
        cong_client_names = self.topo.getCongClients()
        self.cong_clients = []
        for cn in cong_client_names:
            self.cong_clients.append(self.topo.get_host(cn))

        cong_server_names = self.topo.getCongServers()
        self.cong_servers = []
        for sn in cong_server_names:
            self.cong_servers.append(self.topo.get_host(sn))

        i = 0
        netmask = "255.255.255.0"
        links = self.topo.get_link_characteristics()
        for l in self.topo.switch:
            cmd = self.interface_up_command(
                    self.get_client_interface(i),
                    self.getClientIP(i), netmask)
            self.topo.command_to(self.client, cmd)
            clientIntfMac = self.client.intf(self.get_client_interface(i)).MAC()
            self.topo.command_to(self.router, "arp -s " + self.getClientIP(i) + " " + clientIntfMac)

            if(links[i].backup):
                cmd = self.interface_backup_command(
                        self.get_client_interface(i))
                self.topo.command_to(self.client, cmd)

            # Congestion client
            cmd = self.interface_up_command(
                    self.getCongClientInterface(i),
                    self.getCongClientIP(i), netmask)
            self.topo.command_to(self.cong_clients[i], cmd)
            congClientIntfMac = self.cong_clients[i].intf(self.getCongClientInterface(i)).MAC()
            self.topo.command_to(self.router, "arp -s " + self.getCongClientIP(i) + " " + congClientIntfMac)

            cmd = self.interface_up_command(
                    self.get_router_interface_to_switch(i),
                    self.getRouterIPSwitch(i), netmask)
            self.topo.command_to(self.router, cmd)
            routerIntfMac = self.router.intf(self.get_router_interface_to_switch(i)).MAC()
            self.topo.command_to(self.client, "arp -s " + self.getRouterIPSwitch(i) + " " + routerIntfMac)
            # Don't forget the congestion client
            self.topo.command_to(self.cong_clients[i], "arp -s " + self.getRouterIPSwitch(i) + " " + routerIntfMac)
            print(str(links[i]))
            i = i + 1

        cmd = self.interface_up_command(self.getRouterInterfaceServer(),
                self.getRouterIPServer(), netmask)
        self.topo.command_to(self.router, cmd)
        routerIntfMac = self.router.intf(self.getRouterInterfaceServer()).MAC()
        self.topo.command_to(self.server, "arp -s " + self.getRouterIPServer() + " " + routerIntfMac)

        cmd = self.interface_up_command(self.get_server_interface(),
                self.getServerIP(), netmask)
        self.topo.command_to(self.server, cmd)
        serverIntfMac = self.server.intf(self.get_server_interface()).MAC()
        self.topo.command_to(self.router, "arp -s " + self.getServerIP() + " " + serverIntfMac)

        # Congestion servers
        i = 0
        for s in self.cong_servers:
            cmd = self.interface_up_command(self.getRouterInterfaceCongServer(i),
                self.getRouterIPCongServer(i), netmask)
            self.topo.command_to(self.router, cmd)
            routerIntfMac = self.router.intf(self.getRouterInterfaceCongServer(i)).MAC()
            self.topo.command_to(s, "arp -s " + self.getRouterIPCongServer(i) + " " + routerIntfMac)

            cmd = self.interface_up_command(self.getCongServerInterface(i),
                self.getCongServerIP(i), netmask)
            self.topo.command_to(s, cmd)
            congServerIntfMac = s.intf(self.getCongServerInterface(i)).MAC()
            self.topo.command_to(self.router, "arp -s " + self.getCongServerIP(i) + " " + congServerIntfMac)
            i = i + 1

    def getClientIP(self, interfaceID):
        lSubnet = self.param.get(TopoParameter.LEFT_SUBNET)
        clientIP = lSubnet + str(interfaceID) + ".1"
        return clientIP

    def getCongClientIP(self, interfaceID):
        lSubnet = self.param.get(TopoParameter.LEFT_SUBNET)
        congClientIP = lSubnet + str(interfaceID) + ".127"
        return congClientIP

    def getClientSubnet(self, interfaceID):
        lSubnet = self.param.get(TopoParameter.LEFT_SUBNET)
        clientSubnet = lSubnet + str(interfaceID) + ".0/24"
        return clientSubnet

    def getRouterIPSwitch(self, interfaceID):
        lSubnet = self.param.get(TopoParameter.LEFT_SUBNET)
        routerIP = lSubnet + str(interfaceID) + ".2"
        return routerIP

    def getRouterIPServer(self):
        rSubnet = self.param.get(TopoParameter.RIGHT_SUBNET)
        routerIP = rSubnet + "0.2"
        return routerIP

    def getRouterIPCongServer(self, congID):
        rSubnet = self.param.get(TopoParameter.RIGHT_SUBNET)
        routerIP = rSubnet + str(1 + congID) + ".2"
        return routerIP

    def getServerIP(self):
        rSubnet = self.param.get(TopoParameter.RIGHT_SUBNET)
        serverIP = rSubnet + "0.1"
        return serverIP

    def getCongServerIP(self, congID):
        rSubnet = self.param.get(TopoParameter.RIGHT_SUBNET)
        serverIP = rSubnet + str(1 + congID) + ".1"
        return serverIP

    def client_interface_count(self):
        return len(self.topo.switch)

    def getRouterInterfaceServer(self):
        return self.get_router_interface_to_switch(len(self.topo.switch))

    def getRouterInterfaceCongServer(self, congID):
        return self.get_router_interface_to_switch(len(self.topo.switch) + 1 + congID)

    def get_client_interface(self, interfaceID):
        return  Topo.CLIENT_NAME + "-eth" + str(interfaceID)

    def getCongClientInterface(self, interfaceID):
        return MultiInterfaceCongConfig.congClientName + str(interfaceID) + "-eth0"

    def get_router_interface_to_switch(self, interfaceID):
        return  Topo.ROUTER_NAME + "-eth" + str(interfaceID)

    def get_server_interface(self):
        return  Topo.SERVER_NAME + "-eth0"

    def getCongServerInterface(self, interfaceID):
        return MultiInterfaceCongConfig.congServerName + str(interfaceID) + "-eth0"

    def getMidLeftName(self, id):
        return Topo.SWITCH_NAME_PREFIX + str(id)

    def getMidRightName(self, id):
        return Topo.ROUTER_NAME