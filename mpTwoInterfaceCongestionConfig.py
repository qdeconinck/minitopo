from core.topo import Topo, TopoConfig, TopoParameter
from mpTwoInterfaceCongestionTopo import MpTwoInterfaceCongestionTopo

class MpTwoInterfaceCongestionConfig(TopoConfig):
    def __init__(self, topo, param):
        super().__init__(topo, param)

    def configureRoute(self):
        # Client - Router
        cmd = self.addRouteTableCommand("10.0.0.1", 0)
        self.topo.commandTo(self.client, cmd)
        cmd = self.addRouteScopeLinkCommand("10.0.0.0/24", Topo.clientName + "-eth0", 0)
        self.topo.commandTo(self.client, cmd)
        cmd = self.addRouteDefaultCommand("10.0.0.2", 0)
        self.topo.commandTo(self.client, cmd)

        # Client -> Router cong
        cmd = self.addRouteTableCommand("10.0.1.1", 1)
        self.topo.commandTo(self.client, cmd)
        cmd = self.addRouteScopeLinkCommand("10.0.1.0/24", Topo.clientName + "-eth1", 1)
        self.topo.commandTo(self.client, cmd)
        cmd = self.addRouteDefaultCommand("10.0.1.2", 1)
        self.topo.commandTo(self.client, cmd)

        # Client cong -> Router cong
        cmd = self.addRouteTableCommand("10.0.2.1", 0)
        self.topo.commandTo(self.clientCong, cmd)
        cmd = self.addRouteScopeLinkCommand("10.0.2.0/24", Topo.clientName + "Cong-eth0", 0)
        self.topo.commandTo(self.clientCong, cmd)
        cmd = self.addRouteDefaultCommand("10.0.2.2", 0)
        self.topo.commandTo(self.clientCong, cmd)

        # Router cong -> Router
        cmd = self.addRouteTableCommand("10.0.3.1", 0)
        self.topo.commandTo(self.routerCong, cmd)
        cmd = self.addRouteScopeLinkCommand("10.1.0.0/16", Topo.routerName + "Cong-eth2", 0)
        self.topo.commandTo(self.routerCong, cmd)
        cmd = self.addRouteDefaultCommand("10.0.3.2", 0)
        self.topo.commandTo(self.routerCong, cmd)

        # Router -> Router cong
        cmd = self.addRouteTableCommand("10.0.3.2", 0)
        self.topo.commandTo(self.router, cmd)
        cmd = self.addRouteScopeLinkCommand("10.0.0.0/16", Topo.routerName + "-eth1", 0)
        self.topo.commandTo(self.router, cmd)
        cmd = self.addRouteDefaultCommand("10.0.3.1", 0)
        self.topo.commandTo(self.router, cmd)

        # Default route Client
        cmd = self.addRouteDefaultGlobalCommand("10.0.0.2", Topo.clientName + "-eth0")
        self.topo.commandTo(self.client, cmd)

        # Default route Client cong
        cmd = self.addRouteDefaultGlobalCommand("10.0.2.2", Topo.clientName + "Cong-eth0")
        self.topo.commandTo(self.clientCong, cmd)

        # Default route Router cong
        cmd = self.addRouteDefaultGlobalCommand("10.0.3.2", Topo.routerName + "Cong-eth2")
        self.topo.commandTo(self.routerCong, cmd)

        # Default route Router
        cmd = self.addRouteDefaultGlobalCommand("10.0.3.1", Topo.routerName + "-eth1")
        self.topo.commandTo(self.router, cmd)

        # Default route Server
        cmd = self.addRouteDefaultGlobalCommand("10.1.0.2", Topo.serverName + "-eth0")
        self.topo.commandTo(self.server, cmd)

        # Default route Server cong
        cmd = self.addRouteDefaultGlobalCommand("10.1.1.2", Topo.serverName + "Cong-eth0")
        self.topo.commandTo(self.serverCong, cmd)

    def configureInterface(self, srcHost, dstHost, srcInterfaceName, srcIP, netmask):
        cmd = self.interfaceUpCommand(srcInterfaceName, srcIP, netmask)
        self.topo.commandTo(srcHost, cmd)
        mac = srcHost.intf(srcInterfaceName).MAC()
        cmd = self.arpCommand(srcIP, mac)
        self.topo.commandTo(dstHost, cmd)

    def configureInterfaces(self):
        print("Configure interfaces for two inf cong")
        self.client = self.topo.getHost(Topo.clientName)
        self.clientCong = self.topo.getHost(Topo.clientName + "Cong")
        self.server = self.topo.getHost(Topo.serverName)
        self.serverCong = self.topo.getHost(Topo.serverName + "Cong")
        self.router = self.topo.getHost(Topo.routerName)
        self.routerCong = self.topo.getHost(Topo.routerName + "Cong")
        netmask = "255.255.255.0"
        links = self.topo.getLinkCharacteristics()

        # Link 0: Client - Router
        self.configureInterface(self.client, self.router, Topo.clientName + "-eth0", "10.0.0.1", netmask)

        if(links[0].back_up):
            cmd = self.interfaceBUPCommand(Topo.clientName + "-eth0")
            self.topo.commandTo(self.client, cmd)

        self.configureInterface(self.router, self.client, Topo.routerName + "-eth0", "10.0.0.2", netmask)
        print(str(links[0]))

        # Client - Router cong
        self.configureInterface(self.client, self.routerCong, Topo.clientName + "-eth1", "10.0.1.1", netmask)

        if(links[1].back_up):
            cmd = self.interfaceBUPCommand(Topo.clientName + "-eth1")
            self.topo.commandTo(self.client, cmd)

        self.configureInterface(self.routerCong, self.client, Topo.routerName + "Cong-eth0", "10.0.1.2", netmask)

        # Link 1: Router - Router cong
        self.configureInterface(self.routerCong, self.router, Topo.routerName + "Cong-eth2", "10.0.3.1", netmask)
        self.configureInterface(self.router, self.routerCong, Topo.routerName + "-eth1", "10.0.3.2", netmask)
        print(str(links[1]))

        # Link 2: Client cong - Router cong
        self.configureInterface(self.clientCong, self.routerCong, Topo.clientName + "Cong-eth0", "10.0.2.1", netmask)
        self.configureInterface(self.routerCong, self.clientCong, Topo.routerName + "Cong-eth1", "10.0.2.2", netmask)
        print(str(links[2]))

        # Router - Server
        self.configureInterface(self.server, self.router, Topo.serverName + "-eth0", "10.1.0.1", netmask)
        self.configureInterface(self.router, self.server, Topo.routerName + "-eth2", "10.1.0.2", netmask)

        # Router - Server cong
        self.configureInterface(self.serverCong, self.router, Topo.serverName + "Cong-eth0", "10.1.1.1", netmask)
        self.configureInterface(self.router, self.serverCong, Topo.routerName + "-eth3", "10.1.1.2", netmask)

    def getClientIP(self, interfaceID):
        lSubnet = self.param.getParam(TopoParameter.LSUBNET)
        clientIP = lSubnet + str(interfaceID) + ".1"
        return clientIP

    def getClientSubnet(self, interfaceID):
        lSubnet = self.param.getParam(TopoParameter.LSUBNET)
        clientSubnet = lSubnet + str(interfaceID) + ".0/24"
        return clientSubnet

    def getClientCongIP(self):
        lSubnet = self.param.getParam(TopoParameter.LSUBNET)
        clientIP = lSubnet + str(2) + ".1"
        return clientIP

    def getClientCongSubnet(self, interfaceID):
        lSubnet = self.param.getParam(TopoParameter.LSUBNET)
        clientSubnet = lSubnet + str(128) + ".0/24"
        return clientSubnet

    def getRouterIPSwitch(self, interfaceID):
        lSubnet = self.param.getParam(TopoParameter.LSUBNET)
        routerIP = lSubnet + str(interfaceID) + ".2"
        return routerIP

    def getRouterIPServer(self):
        rSubnet = self.param.getParam(TopoParameter.RSUBNET)
        routerIP = rSubnet + "0.2"
        return routerIP

    def getServerIP(self):
        rSubnet = self.param.getParam(TopoParameter.RSUBNET)
        serverIP = rSubnet + "0.1"
        return serverIP

    def getClientInterfaceCount(self):
        return len(self.topo.switch)

    def getRouterInterfaceServer(self):
        return self.getRouterInterfaceSwitch(len(self.topo.switch))

    def getClientInterface(self, interfaceID):
        return Topo.clientName + "-eth" + str(interfaceID)

    def getRouterInterfaceSwitch(self, interfaceID):
        return Topo.routerName + "-eth" + str(interfaceID)

    def getServerInterface(self):
        return Topo.serverName + "-eth0"

    def getMidLeftName(self, id):
        return Topo.switchNamePrefix + str(id)

    def getMidRightName(self, id):
        if id == 2:
            return Topo.routerName + "Cong"

        return Topo.routerName

    def getMidL2RInterface(self, id):
        return self.getMidLeftName(id) + "-eth2"

    def getMidR2LInterface(self, id):
        if id == 2:
            return self.getMidRightName(id) + "-eth1"

        return self.getMidRightName(id) + "-eth" + str(id)
