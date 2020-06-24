from core.topo import Topo

class MpECMPSingleInterfaceTopo(Topo):
    def __init__(self, topoBuilder, parameterFile):
        super().__init__(topoBuilder, parameterFile)

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
            self.addLink(self.rswitch, self.routers[-1], **l.asDict())

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

