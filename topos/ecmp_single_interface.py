from core.topo import Topo, TopoConfig, TopoParameter
from struct import *

class ECMPSingleInterfaceTopo(Topo):
    NAME = "ECMPLike"

    def __init__(self, topoBuilder, parameterFile):
        super(ECMPSingleInterfaceTopo, self).__init__(topoBuilder, parameterFile)

        print("Hello ECMP topo")

        self.client = self.addHost(Topo.clientName)
        self.server = self.addHost(Topo.serverName)
        self.lswitch = self.addSwitch(Topo.switchNamePrefix + "0")
        self.rswitch = self.addSwitch(Topo.switchNamePrefix + "1")

        self.addLink( self.client, self.lswitch)
        self.addLink( self.server, self.rswitch)

        self.routers = []
        for l in self.topoParam.linkCharacteristics:
            self.routers.append(self.addOneRouterPerLink(l))
            print("added : " + self.routers[-1])
            self.addLink(self.lswitch, self.routers[-1])
            self.addLink(self.rswitch, self.routers[-1], **l.as_dict())

    def addOneRouterPerLink(self, link):
        return self.addHost(Topo.routerNamePrefix +
                str(link.id))

    def __str__(self):
        s = "Single if ECMP like env\n"
        i = 0
        n = len(self.topoParam.linkCharacteristics)
        for p in self.topoParam.linkCharacteristics:
            if i == n // 2:
                if n % 2 == 0:
                    s = s + "c---sw          sw-----s\n"
                    s = s + "    |-----R-----|\n"
                else:
                    s = s + "c---sw----R-----sw-----s\n"
            else:
                s = s + "    |-----R-----|\n"

            i = i + 1
        return s


class ECMPSingleInterfaceConfig(TopoConfig):
    NAME = "ECMPLike"

    def __init__(self, topo, param):
        super(ECMPSingleInterfaceConfig, self).__init__(topo, param)

    def configureRoute(self):
        i = 0
        mask = len(self.topo.routers) - 1
        for l in self.topo.routers:
            cmd = self.getIptableRuleICMP(mask, i)
            self.topo.command_to(self.client, cmd)
            self.topo.command_to(self.server, cmd)

            cmd = self.getIptableRuleTCPPortClient(mask, i)
            self.topo.command_to(self.client, cmd)
            cmd = self.getIptableRuleTCPPortServer(mask, i)
            self.topo.command_to(self.server, cmd)

            cmd = self.getIpRuleCmd(i)
            self.topo.command_to(self.client, cmd)
            self.topo.command_to(self.server, cmd)

            cmd = self.getDefaultRouteCmd(self.getRouterIPClient(i),
                    i)
            self.topo.command_to(self.client, cmd)
            cmd = self.getDefaultRouteCmd(self.getRouterIPServer(i),
                    i)
            self.topo.command_to(self.server, cmd)

            i = i + 1

        ###
        cmd = self.addRouteDefaultSimple(self.getRouterIPServer(0))
        self.topo.command_to(self.server, cmd)

        cmd = self.addRouteDefaultSimple(self.getRouterIPClient(0))
        self.topo.command_to(self.client, cmd)

        self.topo.command_to(self.client, "ip route flush cache")
        self.topo.command_to(self.server, "ip route flush cache")

    def getIptableRuleICMP(self, mask, id):
        s = 'iptables -t mangle -A OUTPUT -m u32 --u32 ' + \
                '"6&0xFF=0x1 && ' + \
                '24&0x' + \
                pack('>I',(mask)).encode('hex') + \
                '=0x' + pack('>I',id).encode('hex') + \
                '" -j MARK --set-mark ' + str(id + 1)
        print (s)
        return s

    def getIptableRuleTCPPortClient(self, mask, id):
        s = 'iptables -t mangle -A OUTPUT -m u32 --u32 ' + \
                '"6&0xFF=0x6 && ' + \
                '18&0x' + \
                pack('>I',(mask)).encode('hex') + \
                '=0x' + pack('>I',id).encode('hex') + \
                '" -j MARK --set-mark ' + str(id + 1)
        print (s)
        return s

    def getIptableRuleTCPPortServer(self, mask, id):
        s = 'iptables -t mangle -A OUTPUT -m u32 --u32 ' + \
                '"6&0xFF=0x6 && ' + \
                '20&0x' + \
                pack('>I',(mask)).encode('hex') + \
                '=0x' + pack('>I',id).encode('hex') + \
                '" -j MARK --set-mark ' + str(id + 1)
        print (s)
        return s

    def getIpRuleCmd(self, id):
        s = 'ip rule add fwmark ' + str(id + 1) + ' table ' + \
                str(id + 1)
        print(s)
        return s

    def getDefaultRouteCmd(self, via, id):
        s = 'ip route add default via ' + via + ' table ' + str(id + 1)
        print(s)
        return s

    def configureInterfaces(self):
        self.client = self.topo.get_host(Topo.clientName)
        self.server = self.topo.get_host(Topo.serverName)
        self.routers = []
        i = 0
        netmask = "255.255.255.0"
        for l in self.topo.routers:
            self.routers.append(self.topo.get_host(
                Topo.routerNamePrefix + str(i)))
            cmd = self.interfaceUpCommand(
                    self.getRouterInterfaceLSwitch(i),
                    self.getRouterIPClient(i), netmask)
            self.topo.command_to(self.routers[-1] , cmd)

            cmd = self.interfaceUpCommand(
                    self.getRouterInterfaceRSwitch(i),
                    self.getRouterIPServer(i), netmask)
            self.topo.command_to(self.routers[-1] , cmd)

            i = i + 1

        cmd = self.interfaceUpCommand(self.get_client_interface(0),
                self.getClientIP(0), netmask)
        self.topo.command_to(self.client, cmd)

        cmd = self.interfaceUpCommand(self.getServerInterface(),
                self.getServerIP(), netmask)
        self.topo.command_to(self.server, cmd)

    def getClientIP(self, interfaceID):
        lSubnet = self.param.get(TopoParameter.LSUBNET)
        clientIP = lSubnet + str(interfaceID) + ".1"
        return clientIP

    def getClientSubnet(self, interfaceID):
        lSubnet = self.param.get(TopoParameter.LSUBNET)
        clientSubnet = lSubnet + str(interfaceID) + ".0/24"
        return clientSubnet

    def getRouterIPClient(self, id):
        lSubnet = self.param.get(TopoParameter.LSUBNET)
        routerIP = lSubnet + "0." + str(id + 2)
        return routerIP

    def getRouterIPServer(self, id):
        rSubnet = self.param.get(TopoParameter.RSUBNET)
        routerIP = rSubnet + "0." + str(id + 2)
        return routerIP

    def getServerIP(self):
        rSubnet = self.param.get(TopoParameter.RSUBNET)
        serverIP = rSubnet + "0.1"
        return serverIP

    def client_interface_count(self):
        return 1

    def getRouterInterfaceLSwitch(self, id):
        return  Topo.routerNamePrefix + str(id) + "-eth0"

    def getRouterInterfaceRSwitch(self, id):
        return  Topo.routerNamePrefix + str(id) + "-eth1"

    def get_client_interface(self, interfaceID):
        return  Topo.clientName + "-eth" + str(interfaceID)

    def getServerInterface(self):
        return  Topo.serverName + "-eth0"

    def getMidLeftName(self, id):
        return Topo.routerNamePrefix + str(id)

    def getMidRightName(self, id):
        return Topo.switchNamePrefix + "1"

    def getMidL2RInterface(self, id):
        return self.getMidLeftName(id) + "-eth1"

    def getMidR2LInterface(self, id):
        return self.getMidRightName(id) + "-eth" + str(id+2)
