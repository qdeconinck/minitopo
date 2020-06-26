from core.topo import Topo, TopoConfig, TopoParameter

class MultiInterfaceTopo(Topo):
    NAME = "MultiIf"

    def __init__(self, topoBuilder, parameterFile):
        super(MultiInterfaceTopo, self).__init__(topoBuilder, parameterFile)
        print("Hello from topo multi if")
        self.client = self.addHost(Topo.clientName)
        self.server = self.addHost(Topo.serverName)
        self.router = self.addHost(Topo.routerName)
        self.switchClient = []
        self.switchServer = []
        for l in self.topoParam.linkCharacteristics:
            self.switchClient.append(self.addSwitch1ForLink(l))
            self.addLink(self.client,self.switchClient[-1])
            self.switchServer.append(self.addSwitch2ForLink(l))
            self.addLink(self.switchClient[-1], self.switchServer[-1], **l.asDict())
            self.addLink(self.switchServer[-1],self.router)
        self.addLink(self.router, self.server)

    def addSwitch1ForLink(self, link):
        return self.addSwitch(MultiInterfaceTopo.switchNamePrefix +
                str(2 * link.id))

    def addSwitch2ForLink(self, link):
        return self.addSwitch(MultiInterfaceTopo.switchNamePrefix +
                str(2 * link.id + 1))

    def __str__(self):
        s = "Simple multiple interface topolgy \n"
        i = 0
        n = len(self.topoParam.linkCharacteristics)
        for p in self.topoParam.linkCharacteristics:
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

    def configureRoute(self):
        i = 0
        for l in self.topo.switchClient:
            cmd = self.addRouteTableCommand(self.getClientIP(i), i)
            self.topo.command_to(self.client, cmd)

            cmd = self.addRouteScopeLinkCommand(
                    self.getClientSubnet(i),
                    self.get_client_interface(i), i)
            self.topo.command_to(self.client, cmd)

            cmd = self.addRouteDefaultCommand(self.getRouterIPSwitch(i),
                    i)
            self.topo.command_to(self.client, cmd)
            i = i + 1

        cmd = self.addRouteDefaultGlobalCommand(self.getRouterIPSwitch(0),
                self.get_client_interface(0))
        self.topo.command_to(self.client, cmd)

        cmd = self.addRouteDefaultSimple(self.getRouterIPServer())
        self.topo.command_to(self.server, cmd)


    def configureInterfaces(self):
        print("Configure interfaces for multi inf")
        self.client = self.topo.get_host(Topo.clientName)
        self.server = self.topo.get_host(Topo.serverName)
        self.router = self.topo.get_host(Topo.routerName)
        i = 0
        netmask = "255.255.255.0"
        links = self.topo.getLinkCharacteristics()
        for l in self.topo.switchClient:
            cmd = self.interfaceUpCommand(
                    self.get_client_interface(i),
                    self.getClientIP(i), netmask)
            self.topo.command_to(self.client, cmd)
            clientIntfMac = self.client.intf(self.get_client_interface(i)).MAC()
            self.topo.command_to(self.router, "arp -s " + self.getClientIP(i) + " " + clientIntfMac)

            if(links[i].back_up):
                cmd = self.interface_backup_command(
                        self.get_client_interface(i))
                self.topo.command_to(self.client, cmd)

            i = i + 1

        i = 0
        for l in self.topo.switchServer:
            cmd = self.interfaceUpCommand(
                    self.get_router_interface_to_switch(i),
                    self.getRouterIPSwitch(i), netmask)
            self.topo.command_to(self.router, cmd)
            routerIntfMac = self.router.intf(self.get_router_interface_to_switch(i)).MAC()
            self.topo.command_to(self.client, "arp -s " + self.getRouterIPSwitch(i) + " " + routerIntfMac)
            print(str(links[i]))
            i = i + 1

        cmd = self.interfaceUpCommand(self.getRouterInterfaceServer(),
                self.getRouterIPServer(), netmask)
        self.topo.command_to(self.router, cmd)
        routerIntfMac = self.router.intf(self.getRouterInterfaceServer()).MAC()
        self.topo.command_to(self.server, "arp -s " + self.getRouterIPServer() + " " + routerIntfMac)

        cmd = self.interfaceUpCommand(self.getServerInterface(),
                self.getServerIP(), netmask)
        self.topo.command_to(self.server, cmd)
        serverIntfMac = self.server.intf(self.getServerInterface()).MAC()
        self.topo.command_to(self.router, "arp -s " + self.getServerIP() + " " + serverIntfMac)

    def getClientIP(self, interfaceID):
        lSubnet = self.param.get(TopoParameter.LSUBNET)
        clientIP = lSubnet + str(interfaceID) + ".1"
        return clientIP

    def getClientSubnet(self, interfaceID):
        lSubnet = self.param.get(TopoParameter.LSUBNET)
        clientSubnet = lSubnet + str(interfaceID) + ".0/24"
        return clientSubnet

    def getRouterIPSwitch(self, interfaceID):
        lSubnet = self.param.get(TopoParameter.LSUBNET)
        routerIP = lSubnet + str(interfaceID) + ".2"
        return routerIP

    def getRouterIPServer(self):
        rSubnet = self.param.get(TopoParameter.RSUBNET)
        routerIP = rSubnet + "0.2"
        return routerIP

    def getServerIP(self):
        rSubnet = self.param.get(TopoParameter.RSUBNET)
        serverIP = rSubnet + "0.1"
        return serverIP

    def client_interface_count(self):
        return len(self.topo.switchClient)

    def getRouterInterfaceServer(self):
        return self.get_router_interface_to_switch(len(self.topo.switchServer))

    def get_client_interface(self, interfaceID):
        return  Topo.clientName + "-eth" + str(interfaceID)

    def get_router_interface_to_switch(self, interfaceID):
        return  Topo.routerName + "-eth" + str(interfaceID)

    def getServerInterface(self):
        return  Topo.serverName + "-eth0"

    def getSwitchClientName(self, id):
        return Topo.switchNamePrefix + str(2 * id)

    def getSwitchServerName(self, id):
        return Topo.switchNamePrefix + str(2 * id + 1)

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
