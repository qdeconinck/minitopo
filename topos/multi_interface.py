from core.topo import Topo, TopoConfig, TopoParameter

class MultiInterfaceTopo(Topo):
    NAME = "MultiIf"

    def __init__(self, topo_builder, parameterFile):
        super(MultiInterfaceTopo, self).__init__(topo_builder, parameterFile)
        print("Hello from topo multi if")
        self.client = self.add_host(Topo.CLIENT_NAME)
        self.server = self.add_host(Topo.SERVER_NAME)
        self.router = self.add_host(Topo.ROUTER_NAME)
        self.switchClient = []
        self.switchServer = []
        for l in self.topo_parameter.link_characteristics:
            self.switchClient.append(self.add_switch1ForLink(l))
            self.add_link(self.client,self.switchClient[-1])
            self.switchServer.append(self.add_switch2ForLink(l))
            self.add_link(self.switchClient[-1], self.switchServer[-1], **l.as_dict())
            self.add_link(self.switchServer[-1],self.router)
        self.add_link(self.router, self.server)

    def add_switch1ForLink(self, link):
        return self.add_switch(MultiInterfaceTopo.SWITCH_NAME_PREFIX +
                str(2 * link.id))

    def add_switch2ForLink(self, link):
        return self.add_switch(MultiInterfaceTopo.SWITCH_NAME_PREFIX +
                str(2 * link.id + 1))

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
        i = 0
        for l in self.topo.switchClient:
            cmd = self.add_table_route_command(self.getClientIP(i), i)
            self.topo.command_to(self.client, cmd)

            cmd = self.add_link_scope_route_command(
                    self.getClientSubnet(i),
                    self.get_client_interface(i), i)
            self.topo.command_to(self.client, cmd)

            cmd = self.add_table_default_route_command(self.getRouterIPSwitch(i),
                    i)
            self.topo.command_to(self.client, cmd)
            i = i + 1

        cmd = self.add_global_default_route_command(self.getRouterIPSwitch(0),
                self.get_client_interface(0))
        self.topo.command_to(self.client, cmd)

        cmd = self.add_simple_default_route_command(self.getRouterIPServer())
        self.topo.command_to(self.server, cmd)


    def configure_interfaces(self):
        print("Configure interfaces for multi inf")
        self.client = self.topo.get_host(Topo.CLIENT_NAME)
        self.server = self.topo.get_host(Topo.SERVER_NAME)
        self.router = self.topo.get_host(Topo.ROUTER_NAME)
        i = 0
        netmask = "255.255.255.0"
        links = self.topo.get_link_characteristics()
        for l in self.topo.switchClient:
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

            i = i + 1

        i = 0
        for l in self.topo.switchServer:
            cmd = self.interface_up_command(
                    self.get_router_interface_to_switch(i),
                    self.getRouterIPSwitch(i), netmask)
            self.topo.command_to(self.router, cmd)
            routerIntfMac = self.router.intf(self.get_router_interface_to_switch(i)).MAC()
            self.topo.command_to(self.client, "arp -s " + self.getRouterIPSwitch(i) + " " + routerIntfMac)
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

    def getClientIP(self, interfaceID):
        lSubnet = self.param.get(TopoParameter.LEFT_SUBNET)
        clientIP = lSubnet + str(interfaceID) + ".1"
        return clientIP

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

    def getServerIP(self):
        rSubnet = self.param.get(TopoParameter.RIGHT_SUBNET)
        serverIP = rSubnet + "0.1"
        return serverIP

    def client_interface_count(self):
        return len(self.topo.switchClient)

    def getRouterInterfaceServer(self):
        return self.get_router_interface_to_switch(len(self.topo.switchServer))

    def get_client_interface(self, interfaceID):
        return  Topo.CLIENT_NAME + "-eth" + str(interfaceID)

    def get_router_interface_to_switch(self, interfaceID):
        return  Topo.ROUTER_NAME + "-eth" + str(interfaceID)

    def get_server_interface(self):
        return  Topo.SERVER_NAME + "-eth0"

    def getSwitchClientName(self, id):
        return Topo.SWITCH_NAME_PREFIX + str(2 * id)

    def getSwitchServerName(self, id):
        return Topo.SWITCH_NAME_PREFIX + str(2 * id + 1)

    def getMidLeftName(self, id):
        return self.getSwitchClientName(id)

    def getMidRightName(self, id):
        return self.getSwitchServerName(id)

    def getMidL2RInterface(self, id):
        return self.getMidLeftName(id) + "-eth2"

    def getMidR2LInterface(self, id):
        return self.getMidRightName(id) + "-eth1"

    def getMidL2RIncomingInterface(self, id):
        return self.getMidLeftName(id) + "-eth1"

    def getMidR2LIncomingInterface(self, id):
        return self.getMidRightName(id) + "-eth2"
