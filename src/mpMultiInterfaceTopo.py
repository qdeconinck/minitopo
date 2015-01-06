from mpTopo import MpTopo

class MpMultiInterfaceTopo(MpTopo):
	def __init__(self, topoBuilder, parameterFile):
		MpTopo.__init__(self,topoBuilder, parameterFile)
		print("Hello from topo multi if")
		self.addHost("Client")
		self.addHost("Server")
		for l in self.topoParam.linkCharacteristics:
			self.addOneSwitchPerLink(l)

	def addOneSwitchPerLink(self, link):
		self.addSwitch("sw" + str(link.id))
	
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

