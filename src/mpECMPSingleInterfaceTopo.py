from mpTopo import MpTopo

class MpECMPSingleInterfaceTopo(MpTopo):
	def __init__(self, topoBuilder, parameterFile):
		MpTopo.__init__(self,topoBuilder, parameterFile)
		
		print("Hello ECMP topo")
		
		self.client = self.addHost(MpTopo.clientName)
		self.server = self.addHost(MpTopo.serverName)
		self.lswitch = self.addSwitch(MpTopo.switchNamePrefix + "0")
		self.rswitch = self.addSwitch(MpTopo.switchNamePrefix + "1")
		
		self.addLink( self.client, self.lswitch)
		self.addLink( self.server, self.rswitch)

		self.routers = []
		for l in self.topoParam.linkCharacteristics:
			self.routers.append(self.addOneRouterPerLink(l))
			print("added : " + self.routers[-1])
			self.addLink(self.lswitch, self.routers[-1])
			self.addLink(self.rswitch, self.routers[-1], **l.asDict())

	def addOneRouterPerLink(self, link):
		return self.addHost(MpTopo.routerNamePrefix +
				str(link.id))

	def __str__(self):
		s = "Single if ECMP like env"
		"""
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
		"""

		return s

