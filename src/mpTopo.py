from mpParamTopo import MpParamTopo

class MpTopo:
	mininetBuilder = "mininet"
	multiIfTopo = "MultiIf"
	topoAttr    = "topoType"
	switchNamePrefix = "s"
	routerNamePrefix = "r"
	clientName = "Client"
	serverName = "Server"
	routerName = "Router"
	cmdLog = "command.log"

	"""Simple MpTopo"""
	def __init__(self, topoBuilder, topoParam):
		self.topoBuilder = topoBuilder
		self.topoParam = topoParam
		self.changeNetem = topoParam.getParam(MpParamTopo.changeNetem)
		self.logFile = open(MpTopo.cmdLog, 'w')

	def getLinkCharacteristics(self):
		return self.topoParam.linkCharacteristics

	def commandTo(self, who, cmd):
		self.logFile.write(who.__str__() + " : " + cmd + "\n")
		return self.topoBuilder.commandTo(who, cmd)

	def notNSCommand(self, cmd):
		"""
		mainly use for not namespace sysctl.
		"""
		self.logFile.write("Not_NS" + " : " + cmd + "\n")
		return self.topoBuilder.notNSCommand(cmd)

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

	def closeLogFile(self):
		self.logFile.close()

	def stopNetwork(self):
		self.topoBuilder.stopNetwork()
