from core.topo import Topo

class MpMultiInterfaceTopo(Topo):
    def __init__(self, topoBuilder, parameterFile):
        super(MpMultiInterfaceTopo, self).__init__(topoBuilder, parameterFile)
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
        return self.addSwitch(MpMultiInterfaceTopo.switchNamePrefix +
                str(2 * link.id))

    def addSwitch2ForLink(self, link):
        return self.addSwitch(MpMultiInterfaceTopo.switchNamePrefix +
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

