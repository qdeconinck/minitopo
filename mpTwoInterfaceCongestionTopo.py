from mpTopo import MpTopo


class MpTwoInterfaceCongestionTopo(MpTopo):
    def __init__(self, topoBuilder, parameterFile):
		MpTopo.__init__(self, topoBuilder, parameterFile)

		print("Hello from topo two ifs cong")
		print("Expected topo:")
		print("c1----link0--------------|")
		print("|-------------r1--link1--r2-----s1")
		print("              |          |------s2")
		print("c2----link2----")

		self.client = self.addHost(MpTopo.clientName)
		self.clientCong = self.addHost(MpTopo.clientName + "Cong")
		self.server = self.addHost(MpTopo.serverName)
		self.serverCong = self.addHost(MpTopo.serverName + "Cong")
		self.router = self.addHost(MpTopo.routerName)
		self.routerCong = self.addHost(MpTopo.routerName + "Cong")
		self.switch = []

		# Link between c1 and r2
		self.switch.append(self.addOneSwitchPerLink(self.topoParam.linkCharacteristics[0]))
		self.addLink(self.client, self.switch[-1])
		self.addLink(self.switch[-1], self.router, **self.topoParam.linkCharacteristics[0].asDict())

		# Link between c1 and r1
		self.addLink(self.client, self.routerCong)

		# Link between c2 and r1
		self.switch.append(self.addOneSwitchPerLink(self.topoParam.linkCharacteristics[2]))
		self.addLink(self.clientCong, self.switch[-1])
		self.addLink(self.switch[-1], self.routerCong, **self.topoParam.linkCharacteristics[2].asDict())

		# Link between r1 and r2
		self.switch.append(self.addOneSwitchPerLink(self.topoParam.linkCharacteristics[1]))
		self.addLink(self.routerCong, self.switch[-1])
		self.addLink(self.switch[-1], self.router, **self.topoParam.linkCharacteristics[1].asDict())

		# Link between r2 and s1
		self.addLink(self.router, self.server)

		# Link between r2 and s2
		self.addLink(self.router, self.serverCong)

    def __str__(self):
		s = "Hello from topo two ifs cong \n"
		s = s + "c1----link0--------------| \n"
		s = s + "|-------------r1--link1--r2-----s1 \n"
		s = s + "              |          |------s2 \n"
		s = s + "c2----link2---- \n"
		return s

    def addOneSwitchPerLink(self, link):
		return self.addSwitch(MpTopo.switchNamePrefix + str(link.id))
