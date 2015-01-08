class MpTopo:
	mininetBuilder = "mininet"
	multiIfTopo = "MultiIf"
	topoAttr    = "topoType"
	switchNamePrefix = "s"
	clientName = "Client"
	serverName = "Server"
	routerName = "Router"

	"""Simple MpTopo"""
	def __init__(self, topoBuilder, topoParam):
		self.topoBuilder = topoBuilder
		self.topoParam = topoParam 
	
	def commandTo(self, who, cmd):
		self.topoBuilder.commandTo(who, cmd)

	def getHost(self, who):
		return self.topoBuilder.getHost(who)

	def addHost(self, host):
		return self.topoBuilder.addHost(host)

	def addSwitch(self, switch):
		return self.topoBuilder.addSwitch(switch)

	def addLink(self, fromA, toB, **kwargs):
		self.topoBuilder.addLink(fromA,toB,**kwargs)

	def getCLI(self):
		self.topoBuilder.getCLI()

	def startNetwork(self):
		self.topoBuilder.startNetwork()

	def stopNetwork(self):
		self.topoBuilder.stopNetwork()
