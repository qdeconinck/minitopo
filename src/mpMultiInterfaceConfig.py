from mpConfig import MpConfig
from mpMultiInterfaceTopo import MpMultiInterfaceTopo
from mpParamTopo import MpParamTopo
from mpTopo import MpTopo

class MpMultiInterfaceConfig(MpConfig):
	def __init__(self, topo, param):
		MpConfig.__init__(self, topo, param)

	def configureRoute(self):
		i = 0
		for l in self.topo.switch:
			cmd = self.addRouteTableCommand(self.getClientIP(i), i)
			self.topo.commandTo(self.client, cmd)

			cmd = self.addRouteScopeLinkCommand(
					self.getClientSubnet(i),
					self.getClientInterface(i), i)
			self.topo.commandTo(self.client, cmd)

			cmd = self.addRouteDefaultCommand(self.getRouterIPSwitch(i),
					i)
			self.topo.commandTo(self.client, cmd)
			i = i + 1

		cmd = self.addRouteDefaultGlobalCommand(self.getRouterIPSwitch(0),
				self.getClientInterface(0))
		self.topo.commandTo(self.client, cmd)

		cmd = self.addRouteDefaultSimple(self.getRouterIPServer())
		self.topo.commandTo(self.server, cmd)


	def configureInterfaces(self):
		print("Configure interfaces for multi inf")
		self.client = self.topo.getHost(MpTopo.clientName)
		self.server = self.topo.getHost(MpTopo.serverName)
		self.router = self.topo.getHost(MpTopo.routerName)
		i = 0
		netmask = "255.255.255.0"
		links = self.topo.getLinkCharacteristics()
		for l in self.topo.switch:
			cmd = self.interfaceUpCommand(
					self.getClientInterface(i),
					self.getClientIP(i), netmask)
			self.topo.commandTo(self.client, cmd)
			clientIntfMac = self.client.intf(self.getClientInterface(i)).MAC()
			self.topo.commandTo(self.router, "arp -s " + self.getClientIP(i) + " " + clientIntfMac)

			if(links[i].back_up):
				cmd = self.interfaceBUPCommand(
						self.getClientInterface(i))
				self.topo.commandTo(self.client, cmd)

			cmd = self.interfaceUpCommand(
					self.getRouterInterfaceSwitch(i),
					self.getRouterIPSwitch(i), netmask)
			self.topo.commandTo(self.router, cmd)
			routerIntfMac = self.router.intf(self.getRouterInterfaceSwitch(i)).MAC()
			self.topo.commandTo(self.client, "arp -s " + self.getRouterIPSwitch(i) + " " + routerIntfMac)
			print(str(links[i]))
			i = i + 1

		cmd = self.interfaceUpCommand(self.getRouterInterfaceServer(),
				self.getRouterIPServer(), netmask)
		self.topo.commandTo(self.router, cmd)
		routerIntfMac = self.router.intf(self.getRouterInterfaceServer()).MAC()
		self.topo.commandTo(self.server, "arp -s " + self.getRouterIPServer() + " " + routerIntfMac)

		cmd = self.interfaceUpCommand(self.getServerInterface(),
				self.getServerIP(), netmask)
		self.topo.commandTo(self.server, cmd)
		serverIntfMac = self.server.intf(self.getServerInterface()).MAC()
		self.topo.commandTo(self.router, "arp -s " + self.getServerIP() + " " + serverIntfMac)

	def getClientIP(self, interfaceID):
		lSubnet = self.param.getParam(MpParamTopo.LSUBNET)
		clientIP = lSubnet + str(interfaceID) + ".1"
		return clientIP

	def getClientSubnet(self, interfaceID):
		lSubnet = self.param.getParam(MpParamTopo.LSUBNET)
		clientSubnet = lSubnet + str(interfaceID) + ".0/24"
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
		return  MpTopo.clientName + "-eth" + str(interfaceID)

	def getRouterInterfaceSwitch(self, interfaceID):
		return  MpTopo.routerName + "-eth" + str(interfaceID)

	def getServerInterface(self):
		return  MpTopo.serverName + "-eth0"

	def getMidLeftName(self, id):
		return MpTopo.switchNamePrefix + str(id)

	def getMidRightName(self, id):
		return MpTopo.routerName

	def getMidL2RInterface(self, id):
		return self.getMidLeftName(id) + "-eth2"

	def getMidR2LInterface(self, id):
		return self.getMidRightName(id) + "-eth" + str(id)
