from mpConfig import MpConfig
from mpTwoInterfaceCongestionTopo import MpTwoInterfaceCongestionTopo
from mpParamTopo import MpParamTopo
from mpTopo import MpTopo


class MpTwoInterfaceCongestionConfig(MpConfig):
	def __init__(self, topo, param):
		MpConfig.__init__(self, topo, param)

	def configureRoute(self):
		# Client - Router
		cmd = self.addRouteTableCommand("10.0.0.1", 0)
		self.topo.commandTo(self.client, cmd)
		cmd = self.addRouteScopeLinkCommand("10.0.0.0/24", MpTopo.clientName + "-eth0", 0)
		self.topo.commandTo(self.client, cmd)
		cmd = self.addRouteDefaultCommand("10.0.0.2", 0)
		self.topo.commandTo(self.client, cmd)

		# Client -> Router cong
		cmd = self.addRouteTableCommand("10.0.1.1", 1)
		self.topo.commandTo(self.client, cmd)
		cmd = self.addRouteScopeLinkCommand("10.0.1.0/24", MpTopo.clientName + "-eth1", 1)
		self.topo.commandTo(self.client, cmd)
		cmd = self.addRouteDefaultCommand("10.0.1.2", 1)
		self.topo.commandTo(self.client, cmd)

		# Client cong -> Router cong
		cmd = self.addRouteTableCommand("10.0.2.1", 0)
		self.topo.commandTo(self.clientCong, cmd)
		cmd = self.addRouteScopeLinkCommand("10.0.2.0/24", MpTopo.clientName + "Cong-eth0", 0)
		self.topo.commandTo(self.clientCong, cmd)
		cmd = self.addRouteDefaultCommand("10.0.2.2", 0)
		self.topo.commandTo(self.clientCong, cmd)

		# Router cong -> Router
		cmd = self.addRouteTableCommand("10.0.3.1", 0)
		self.topo.commandTo(self.routerCong, cmd)
		cmd = self.addRouteScopeLinkCommand("10.1.0.0/16", MpTopo.routerName + "Cong-eth2", 0)
		self.topo.commandTo(self.routerCong, cmd)
		cmd = self.addRouteDefaultCommand("10.0.3.2", 0)
		self.topo.commandTo(self.routerCong, cmd)

		# Router -> Router cong
		cmd = self.addRouteTableCommand("10.0.3.2", 0)
		self.topo.commandTo(self.router, cmd)
		cmd = self.addRouteScopeLinkCommand("10.0.0.0/16", MpTopo.routerName + "-eth1", 0)
		self.topo.commandTo(self.router, cmd)
		cmd = self.addRouteDefaultCommand("10.0.3.1", 0)
		self.topo.commandTo(self.router, cmd)

		# Default route Client
		cmd = self.addRouteDefaultGlobalCommand("10.0.0.2", MpTopo.clientName + "-eth0")
		self.topo.commandTo(self.client, cmd)

		# Default route Client cong
		cmd = self.addRouteDefaultGlobalCommand("10.0.2.2", MpTopo.clientName + "Cong-eth0")
		self.topo.commandTo(self.clientCong, cmd)

		# Default route Router cong
		cmd = self.addRouteDefaultGlobalCommand("10.0.3.2", MpTopo.routerName + "Cong-eth2")
		self.topo.commandTo(self.routerCong, cmd)

		# Default route Router
		cmd = self.addRouteDefaultGlobalCommand("10.0.3.1", MpTopo.routerName + "-eth1")
		self.topo.commandTo(self.router, cmd)

		# Default route Server
		cmd = self.addRouteDefaultGlobalCommand("10.1.0.2", MpTopo.serverName + "-eth0")
		self.topo.commandTo(self.server, cmd)

		# Default route Server cong
		cmd = self.addRouteDefaultGlobalCommand("10.1.1.2", MpTopo.serverName + "Cong-eth0")
		self.topo.commandTo(self.serverCong, cmd)

	def configureInterface(self, srcHost, dstHost, srcInterfaceName, srcIP, netmask):
		cmd = self.interfaceUpCommand(srcInterfaceName, srcIP, netmask)
		self.topo.commandTo(srcHost, cmd)
		mac = srcHost.intf(srcInterfaceName).MAC()
		cmd = self.arpCommand(srcIP, mac)
		self.topo.commandTo(dstHost, cmd)

	def configureInterfaces(self):
		print("Configure interfaces for two inf cong")
		self.client = self.topo.getHost(MpTopo.clientName)
		self.clientCong = self.topo.getHost(MpTopo.clientName + "Cong")
		self.server = self.topo.getHost(MpTopo.serverName)
		self.serverCong = self.topo.getHost(MpTopo.serverName + "Cong")
		self.router = self.topo.getHost(MpTopo.routerName)
		self.routerCong = self.topo.getHost(MpTopo.routerName + "Cong")
		netmask = "255.255.255.0"
		links = self.topo.getLinkCharacteristics()

		# Link 0: Client - Router
		self.configureInterface(self.client, self.router, MpTopo.clientName + "-eth0", "10.0.0.1", netmask)

		if(links[0].back_up):
			cmd = self.interfaceBUPCommand(MpTopo.clientName + "-eth0")
			self.topo.commandTo(self.client, cmd)

		self.configureInterface(self.router, self.client, MpTopo.routerName + "-eth0", "10.0.0.2", netmask)
		print(str(links[0]))

		# Client - Router cong
		self.configureInterface(self.client, self.routerCong, MpTopo.clientName + "-eth1", "10.0.1.1", netmask)

		if(links[1].back_up):
			cmd = self.interfaceBUPCommand(MpTopo.clientName + "-eth1")
			self.topo.commandTo(self.client, cmd)

		self.configureInterface(self.routerCong, self.client, MpTopo.routerName + "Cong-eth0", "10.0.1.2", netmask)

		# Link 1: Router - Router cong
		self.configureInterface(self.routerCong, self.router, MpTopo.routerName + "Cong-eth2", "10.0.3.1", netmask)
		self.configureInterface(self.router, self.routerCong, MpTopo.routerName + "-eth1", "10.0.3.2", netmask)
		print(str(links[1]))

		# Link 2: Client cong - Router cong
		self.configureInterface(self.clientCong, self.routerCong, MpTopo.clientName + "Cong-eth0", "10.0.2.1", netmask)
		self.configureInterface(self.routerCong, self.clientCong, MpTopo.routerName + "Cong-eth1", "10.0.2.2", netmask)
		print(str(links[2]))

		# Router - Server
		self.configureInterface(self.server, self.router, MpTopo.serverName + "-eth0", "10.1.0.1", netmask)
		self.configureInterface(self.router, self.server, MpTopo.routerName + "-eth2", "10.1.0.2", netmask)

		# Router - Server cong
		self.configureInterface(self.serverCong, self.router, MpTopo.serverName + "Cong-eth0", "10.1.1.1", netmask)
		self.configureInterface(self.router, self.serverCong, MpTopo.routerName + "-eth3", "10.1.1.2", netmask)

	def getClientIP(self, interfaceID):
		lSubnet = self.param.getParam(MpParamTopo.LSUBNET)
		clientIP = lSubnet + str(interfaceID) + ".1"
		return clientIP

	def getClientSubnet(self, interfaceID):
		lSubnet = self.param.getParam(MpParamTopo.LSUBNET)
		clientSubnet = lSubnet + str(interfaceID) + ".0/24"
		return clientSubnet

	def getClientCongIP(self):
		lSubnet = self.param.getParam(MpParamTopo.LSUBNET)
		clientIP = lSubnet + str(2) + ".1"
		return clientIP

	def getClientCongSubnet(self, interfaceID):
		lSubnet = self.param.getParam(MpParamTopo.LSUBNET)
		clientSubnet = lSubnet + str(128) + ".0/24"
		return clientSubnet

	def getRouterIPSwitch(self, interfaceID):
		lSubnet = self.param.getParam(MpParamTopo.LSUBNET)
		routerIP = lSubnet + str(interfaceID) + ".2"
		return routerIP

	def getRouterIPServer(self):
		rSubnet = self.param.getParam(MpParamTopo.RSUBNET)
		routerIP = rSubnet + "0.2"
		return routerIP

	def getServerIP(self):
		rSubnet = self.param.getParam(MpParamTopo.RSUBNET)
		serverIP = rSubnet + "0.1"
		return serverIP

	def getClientInterfaceCount(self):
		return len(self.topo.switch)

	def getRouterInterfaceServer(self):
		return self.getRouterInterfaceSwitch(len(self.topo.switch))

	def getClientInterface(self, interfaceID):
		return MpTopo.clientName + "-eth" + str(interfaceID)

	def getRouterInterfaceSwitch(self, interfaceID):
		return MpTopo.routerName + "-eth" + str(interfaceID)

	def getServerInterface(self):
		return MpTopo.serverName + "-eth0"

	def getMidLeftName(self, id):
		return MpTopo.switchNamePrefix + str(id)

	def getMidRightName(self, id):
		if id == 2:
			return MpTopo.routerName + "Cong"

		return MpTopo.routerName

	def getMidL2RInterface(self, id):
		return self.getMidLeftName(id) + "-eth2"

	def getMidR2LInterface(self, id):
		if id == 2:
			return self.getMidRightName(id) + "-eth1"

		return self.getMidRightName(id) + "-eth" + str(id)
