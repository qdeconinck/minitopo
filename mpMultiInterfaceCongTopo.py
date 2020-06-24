from core.topo import Topo

class MpMultiInterfaceCongTopo(Topo):
    congClientName = "CCli"
    congServerName = "CSer"

    def __init__(self, topoBuilder, parameterFile):
        super().__init__(topoBuilder, parameterFile)
        print("Hello from topo multi if")
        self.client = self.addHost(Topo.clientName)
        self.server = self.addHost(Topo.serverName)
        self.router = self.addHost(Topo.routerName)
        self.cong_clients = []
        self.cong_servers = []
        self.switch = []
        for l in self.topoParam.linkCharacteristics:
            self.switch.append(self.addOneSwitchPerLink(l))
            self.addLink(self.client,self.switch[-1])
            self.cong_clients.append(self.addHost(MpMultiInterfaceCongTopo.congClientName + str(len(self.cong_clients))))
            self.addLink(self.cong_clients[-1], self.switch[-1])
            self.addLink(self.switch[-1],self.router, **l.asDict())
        self.addLink(self.router, self.server)
        for i in range(len(self.cong_clients)):
            self.cong_servers.append(self.addHost(MpMultiInterfaceCongTopo.congServerName + str(len(self.cong_servers))))
            self.addLink(self.router, self.cong_servers[-1])

    def getCongClients(self):
        return self.cong_clients

    def getCongServers(self):
        return self.cong_servers

    def addOneSwitchPerLink(self, link):
        return self.addSwitch(MpMultiInterfaceCongTopo.switchNamePrefix +
                str(link.id))

    def __str__(self):
        s = "Simple multiple interface topology with congestion \n"
        i = 0
        n = len(self.topoParam.linkCharacteristics)
        for p in self.topoParam.linkCharacteristics:
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
