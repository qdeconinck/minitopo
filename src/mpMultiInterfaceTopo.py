from mpTopo import MpTopo

class MpMultiInterfaceTopo(MpTopo):
	def __init__(self, topoBuilder, parameterFile):
		MpTopo.__init__(self,topoBuilder, parameterFile)
		print("Hello from topo multi if")
		self.client = self.addHost(MpTopo.clientName)
		self.server = self.addHost(MpTopo.serverName)
		self.router = self.addHost(MpTopo.routerName)
		self.switch = []
		for l in self.topoParam.linkCharacteristics:
			self.switch.append(self.addOneSwitchPerLink(l))
			self.addLink(self.client,self.switch[-1])
			self.addLink(self.switch[-1],self.router, **l.asDict())
		self.addLink(self.router, self.server)

	def addOneSwitchPerLink(self, link):
		return self.addSwitch(MpMultiInterfaceTopo.switchNamePrefix +
				str(link.id))

	def __str__(self):
		s = "Simple multiple interface topolgy \n"
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

