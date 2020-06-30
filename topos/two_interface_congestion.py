from core.topo import Topo, TopoConfig, TopoParameter


class TwoInterfaceCongestionTopo(Topo):
    NAME = "twoIfCong"

    def __init__(self, topo_builder, parameterFile):
        raise Exception("Broken")
        super(TwoInterfaceCongestionTopo, self).__init__(topo_builder, parameterFile)

        print("Hello from topo two ifs cong")
        print("Expected topo:")
        print("c1----link0--------------|")
        print("|-------------r1--link1--r2-----s1")
        print("              |          |------s2")
        print("c2----link2----")

        self.client = self.add_host(Topo.CLIENT_NAME)
        self.clientCong = self.add_host(Topo.CLIENT_NAME + "Cong")
        self.server = self.add_host(Topo.SERVER_NAME)
        self.serverCong = self.add_host(Topo.SERVER_NAME + "Cong")
        self.router = self.add_host(Topo.ROUTER_NAME)
        self.routerCong = self.add_host(Topo.ROUTER_NAME + "Cong")
        self.switch = []

        # Link between c1 and r2
        self.switch.append(self.addOneSwitchPerLink(self.topo_parameter.link_characteristics[0]))
        self.add_link(self.client, self.switch[-1])
        self.add_link(self.switch[-1], self.router, **self.topo_parameter.link_characteristics[0].as_dict())

        # Link between c1 and r1
        self.add_link(self.client, self.routerCong)

        # Link between c2 and r1
        self.switch.append(self.addOneSwitchPerLink(self.topo_parameter.link_characteristics[2]))
        self.add_link(self.clientCong, self.switch[-1])
        self.add_link(self.switch[-1], self.routerCong, **self.topo_parameter.link_characteristics[2].as_dict())

        # Link between r1 and r2
        self.switch.append(self.addOneSwitchPerLink(self.topo_parameter.link_characteristics[1]))
        self.add_link(self.routerCong, self.switch[-1])
        self.add_link(self.switch[-1], self.router, **self.topo_parameter.link_characteristics[1].as_dict())

        # Link between r2 and s1
        self.add_link(self.router, self.server)

        # Link between r2 and s2
        self.add_link(self.router, self.serverCong)

    def __str__(self):
        s = "Hello from topo two ifs cong \n"
        s = s + "c1----link0--------------| \n"
        s = s + "|-------------r1--link1--r2-----s1 \n"
        s = s + "              |          |------s2 \n"
        s = s + "c2----link2---- \n"
        return s

    def addOneSwitchPerLink(self, link):
        return self.add_switch(Topo.SWITCH_NAME_PREFIX + str(link.id))


class TwoInterfaceCongestionConfig(TopoConfig):
    NAME = "twoIfCong"

    def __init__(self, topo, param):
        super(TwoInterfaceCongestionConfig, self).__init__(topo, param)

    def configure_routing(self):
        # Client - Router
        cmd = self.add_table_route_command("10.0.0.1", 0)
        self.topo.command_to(self.client, cmd)
        cmd = self.add_link_scope_route_command("10.0.0.0/24", Topo.CLIENT_NAME + "-eth0", 0)
        self.topo.command_to(self.client, cmd)
        cmd = self.add_table_default_route_command("10.0.0.2", 0)
        self.topo.command_to(self.client, cmd)

        # Client -> Router cong
        cmd = self.add_table_route_command("10.0.1.1", 1)
        self.topo.command_to(self.client, cmd)
        cmd = self.add_link_scope_route_command("10.0.1.0/24", Topo.CLIENT_NAME + "-eth1", 1)
        self.topo.command_to(self.client, cmd)
        cmd = self.add_table_default_route_command("10.0.1.2", 1)
        self.topo.command_to(self.client, cmd)

        # Client cong -> Router cong
        cmd = self.add_table_route_command("10.0.2.1", 0)
        self.topo.command_to(self.clientCong, cmd)
        cmd = self.add_link_scope_route_command("10.0.2.0/24", Topo.CLIENT_NAME + "Cong-eth0", 0)
        self.topo.command_to(self.clientCong, cmd)
        cmd = self.add_table_default_route_command("10.0.2.2", 0)
        self.topo.command_to(self.clientCong, cmd)

        # Router cong -> Router
        cmd = self.add_table_route_command("10.0.3.1", 0)
        self.topo.command_to(self.routerCong, cmd)
        cmd = self.add_link_scope_route_command("10.1.0.0/16", Topo.ROUTER_NAME + "Cong-eth2", 0)
        self.topo.command_to(self.routerCong, cmd)
        cmd = self.add_table_default_route_command("10.0.3.2", 0)
        self.topo.command_to(self.routerCong, cmd)

        # Router -> Router cong
        cmd = self.add_table_route_command("10.0.3.2", 0)
        self.topo.command_to(self.router, cmd)
        cmd = self.add_link_scope_route_command("10.0.0.0/16", Topo.ROUTER_NAME + "-eth1", 0)
        self.topo.command_to(self.router, cmd)
        cmd = self.add_table_default_route_command("10.0.3.1", 0)
        self.topo.command_to(self.router, cmd)

        # Default route Client
        cmd = self.add_global_default_route_command("10.0.0.2", Topo.CLIENT_NAME + "-eth0")
        self.topo.command_to(self.client, cmd)

        # Default route Client cong
        cmd = self.add_global_default_route_command("10.0.2.2", Topo.CLIENT_NAME + "Cong-eth0")
        self.topo.command_to(self.clientCong, cmd)

        # Default route Router cong
        cmd = self.add_global_default_route_command("10.0.3.2", Topo.ROUTER_NAME + "Cong-eth2")
        self.topo.command_to(self.routerCong, cmd)

        # Default route Router
        cmd = self.add_global_default_route_command("10.0.3.1", Topo.ROUTER_NAME + "-eth1")
        self.topo.command_to(self.router, cmd)

        # Default route Server
        cmd = self.add_global_default_route_command("10.1.0.2", Topo.SERVER_NAME + "-eth0")
        self.topo.command_to(self.server, cmd)

        # Default route Server cong
        cmd = self.add_global_default_route_command("10.1.1.2", Topo.SERVER_NAME + "Cong-eth0")
        self.topo.command_to(self.serverCong, cmd)

    def configureInterface(self, srcHost, dstHost, srcInterfaceName, srcIP, netmask):
        cmd = self.interface_up_command(srcInterfaceName, srcIP, netmask)
        self.topo.command_to(srcHost, cmd)
        mac = srcHost.intf(srcInterfaceName).MAC()
        cmd = self.arp_command(srcIP, mac)
        self.topo.command_to(dstHost, cmd)

    def configure_interfaces(self):
        print("Configure interfaces for two inf cong")
        self.client = self.topo.get_host(Topo.CLIENT_NAME)
        self.clientCong = self.topo.get_host(Topo.CLIENT_NAME + "Cong")
        self.server = self.topo.get_host(Topo.SERVER_NAME)
        self.serverCong = self.topo.get_host(Topo.SERVER_NAME + "Cong")
        self.router = self.topo.get_host(Topo.ROUTER_NAME)
        self.routerCong = self.topo.get_host(Topo.ROUTER_NAME + "Cong")
        netmask = "255.255.255.0"
        links = self.topo.get_link_characteristics()

        # Link 0: Client - Router
        self.configureInterface(self.client, self.router, Topo.CLIENT_NAME + "-eth0", "10.0.0.1", netmask)

        if(links[0].backup):
            cmd = self.interface_backup_command(Topo.CLIENT_NAME + "-eth0")
            self.topo.command_to(self.client, cmd)

        self.configureInterface(self.router, self.client, Topo.ROUTER_NAME + "-eth0", "10.0.0.2", netmask)
        print(str(links[0]))

        # Client - Router cong
        self.configureInterface(self.client, self.routerCong, Topo.CLIENT_NAME + "-eth1", "10.0.1.1", netmask)

        if(links[1].backup):
            cmd = self.interface_backup_command(Topo.CLIENT_NAME + "-eth1")
            self.topo.command_to(self.client, cmd)

        self.configureInterface(self.routerCong, self.client, Topo.ROUTER_NAME + "Cong-eth0", "10.0.1.2", netmask)

        # Link 1: Router - Router cong
        self.configureInterface(self.routerCong, self.router, Topo.ROUTER_NAME + "Cong-eth2", "10.0.3.1", netmask)
        self.configureInterface(self.router, self.routerCong, Topo.ROUTER_NAME + "-eth1", "10.0.3.2", netmask)
        print(str(links[1]))

        # Link 2: Client cong - Router cong
        self.configureInterface(self.clientCong, self.routerCong, Topo.CLIENT_NAME + "Cong-eth0", "10.0.2.1", netmask)
        self.configureInterface(self.routerCong, self.clientCong, Topo.ROUTER_NAME + "Cong-eth1", "10.0.2.2", netmask)
        print(str(links[2]))

        # Router - Server
        self.configureInterface(self.server, self.router, Topo.SERVER_NAME + "-eth0", "10.1.0.1", netmask)
        self.configureInterface(self.router, self.server, Topo.ROUTER_NAME + "-eth2", "10.1.0.2", netmask)

        # Router - Server cong
        self.configureInterface(self.serverCong, self.router, Topo.SERVER_NAME + "Cong-eth0", "10.1.1.1", netmask)
        self.configureInterface(self.router, self.serverCong, Topo.ROUTER_NAME + "-eth3", "10.1.1.2", netmask)

    def get_client_ip(self, interfaceID):
        lSubnet = self.param.get(TopoParameter.LEFT_SUBNET)
        clientIP = lSubnet + str(interfaceID) + ".1"
        return clientIP

    def getClientSubnet(self, interfaceID):
        lSubnet = self.param.get(TopoParameter.LEFT_SUBNET)
        clientSubnet = lSubnet + str(interfaceID) + ".0/24"
        return clientSubnet

    def getClientCongIP(self):
        lSubnet = self.param.get(TopoParameter.LEFT_SUBNET)
        clientIP = lSubnet + str(2) + ".1"
        return clientIP

    def getClientCongSubnet(self, interfaceID):
        lSubnet = self.param.get(TopoParameter.LEFT_SUBNET)
        clientSubnet = lSubnet + str(128) + ".0/24"
        return clientSubnet

    def getRouterIPSwitch(self, interfaceID):
        lSubnet = self.param.get(TopoParameter.LEFT_SUBNET)
        routerIP = lSubnet + str(interfaceID) + ".2"
        return routerIP

    def getRouterIPServer(self):
        rSubnet = self.param.get(TopoParameter.RIGHT_SUBNET)
        routerIP = rSubnet + "0.2"
        return routerIP

    def get_server_ip(self):
        rSubnet = self.param.get(TopoParameter.RIGHT_SUBNET)
        serverIP = rSubnet + "0.1"
        return serverIP

    def client_interface_count(self):
        return len(self.topo.switch)

    def get_router_interface_to_server(self):
        return self.get_router_interface_to_switch(len(self.topo.switch))

    def get_client_interface(self, interfaceID):
        return Topo.CLIENT_NAME + "-eth" + str(interfaceID)

    def get_router_interface_to_switch(self, interfaceID):
        return Topo.ROUTER_NAME + "-eth" + str(interfaceID)

    def get_server_interface(self):
        return Topo.SERVER_NAME + "-eth0"

    def getMidLeftName(self, id):
        return Topo.SWITCH_NAME_PREFIX + str(id)

    def getMidRightName(self, id):
        if id == 2:
            return Topo.ROUTER_NAME + "Cong"

        return Topo.ROUTER_NAME
