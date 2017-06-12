from mpConfig import MpConfig
from mpMultiInterfaceCongTopo import MpMultiInterfaceCongTopo
from mpParamTopo import MpParamTopo
from mpTopo import MpTopo

class MpMultiInterfaceCongConfig(MpConfig):
	def __init__(self, topo, param):
		MpConfig.__init__(self, topo, param)

	def configureRoute(self):
		i = 0
		for l in self.topo.switch:
			cmd = self.addRouteTableCommand(self.getClientIP(i), i)
			self.topo.commandTo(self.client, cmd)

			# Congestion client
			cmd = self.addRouteTableCommand(self.getCongClientIP(i), i)
			self.topo.commandTo(self.cong_clients[i], cmd)

			cmd = self.addRouteScopeLinkCommand(
					self.getClientSubnet(i),
					self.getClientInterface(i), i)
			self.topo.commandTo(self.client, cmd)

			# Congestion client
			cmd = self.addRouteScopeLinkCommand(
					self.getClientSubnet(i),
					self.getCongClientInterface(i), i)
			self.topo.commandTo(self.cong_clients[i], cmd)

			cmd = self.addRouteDefaultCommand(self.getRouterIPSwitch(i),
					i)
			self.topo.commandTo(self.client, cmd)

			# Congestion client
			# Keep the same command
			self.topo.commandTo(self.cong_clients[i], cmd)

			# Congestion client
			cmd = self.addRouteDefaultGlobalCommand(self.getRouterIPSwitch(i),
					self.getCongClientInterface(i))
			i = i + 1

		cmd = self.addRouteDefaultGlobalCommand(self.getRouterIPSwitch(0),
				self.getClientInterface(0))
		self.topo.commandTo(self.client, cmd)

		cmd = self.addRouteDefaultSimple(self.getRouterIPServer())
		self.topo.commandTo(self.server, cmd)
		# Do the same command for all congestion servers
		for s in self.cong_servers:
			self.topo.commandTo(s, cmd)


	def configureInterfaces(self):
		print("Configure interfaces for multi inf")
		self.client = self.topo.getHost(MpTopo.clientName)
		self.server = self.topo.getHost(MpTopo.serverName)
		self.router = self.topo.getHost(MpTopo.routerName)
		cong_client_names = self.topo.getCongClients()
		self.cong_clients = []
		for cn in cong_client_names:
			self.cong_clients.append(self.topo.getHost(cn))

		cong_server_names = self.topo.getCongServers()
		self.cong_servers = []
		for sn in cong_server_names:
			self.cong_servers.append(self.topo.getHost(sn))

		i = 0
		netmask = "255.255.255.0"
		links = self.topo.getLinkCharacteristics()
		# TODO CONGGESTION CONTROL XXX
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

			# Congestion client
			cmd = self.interfaceUpCommand(
					self.getCongClientInterface(i),
					self.getCongClientIP(i), netmask)
			self.topo.commandTo(self.cong_clients[i], cmd)
			congClientIntfMac = self.cong_clients[i].intf(self.getCongClientInterface(i)).MAC()
			self.topo.commandTo(self.router, "arp -s " + self.getCongClientIP(i) + " " + congClientIntfMac)

			cmd = self.interfaceUpCommand(
					self.getRouterInterfaceSwitch(i),
					self.getRouterIPSwitch(i), netmask)
			self.topo.commandTo(self.router, cmd)
			routerIntfMac = self.router.intf(self.getRouterInterfaceSwitch(i)).MAC()
			self.topo.commandTo(self.client, "arp -s " + self.getRouterIPSwitch(i) + " " + routerIntfMac)
			# Don't forget the congestion client
			self.topo.commandTo(self.cong_clients[i], "arp -s " + self.getRouterIPSwitch(i) + " " + routerIntfMac)
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

		# Congestion servers
		i = 0
		for s in self.cong_servers:
			cmd = self.interfaceUpCommand(self.getRouterInterfaceCongServer(i),
				self.getRouterIPCongServer(i), netmask)
			self.topo.commandTo(self.router, cmd)
			routerIntfMac = self.router.intf(self.getRouterInterfaceCongServer(i)).MAC()
			self.topo.commandTo(s, "arp -s " + self.getRouterIPCongServer(i) + " " + routerIntfMac)

			cmd = self.interfaceUpCommand(self.getCongServerInterface(i),
				self.getCongServerIP(i), netmask)
			self.topo.commandTo(s, cmd)
			congServerIntfMac = s.intf(self.getCongServerInterface(i)).MAC()
			self.topo.commandTo(self.router, "arp -s " + self.getCongServerIP(i) + " " + congServerIntfMac)
			i = i + 1

	def getClientIP(self, interfaceID):
		lSubnet = self.param.getParam(MpParamTopo.LSUBNET)
		clientIP = lSubnet + str(interfaceID) + ".1"
		return clientIP

	def getCongClientIP(self, interfaceID):
		lSubnet = self.param.getParam(MpParamTopo.LSUBNET)
		congClientIP = lSubnet + str(interfaceID) + ".127"
		return congClientIP

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

	def getRouterIPCongServer(self, congID):
		rSubnet = self.param.getParam(MpParamTopo.RSUBNET)
		routerIP = rSubnet + str(1 + congID) + ".2"
		return routerIP

	def getServerIP(self):
		rSubnet = self.param.getParam(MpParamTopo.RSUBNET)
		serverIP = rSubnet + "0.1"
		return serverIP

	def getCongServerIP(self, congID):
		rSubnet = self.param.getParam(MpParamTopo.RSUBNET)
		serverIP = rSubnet + str(1 + congID) + ".1"
		return serverIP

	def getClientInterfaceCount(self):
		return len(self.topo.switch)

	def getRouterInterfaceServer(self):
		return self.getRouterInterfaceSwitch(len(self.topo.switch))

	def getRouterInterfaceCongServer(self, congID):
		return self.getRouterInterfaceSwitch(len(self.topo.switch) + 1 + congID)

	def getClientInterface(self, interfaceID):
		return  MpTopo.clientName + "-eth" + str(interfaceID)

	def getCongClientInterface(self, interfaceID):
		return MpMultiInterfaceCongTopo.congClientName + str(interfaceID) + "-eth0"

	def getRouterInterfaceSwitch(self, interfaceID):
		return  MpTopo.routerName + "-eth" + str(interfaceID)

	def getServerInterface(self):
		return  MpTopo.serverName + "-eth0"

	def getCongServerInterface(self, interfaceID):
		return MpMultiInterfaceCongTopo.congServerName + str(interfaceID) + "-eth0"

	def getMidLeftName(self, id):
		return MpTopo.switchNamePrefix + str(id)

	def getMidRightName(self, id):
		return MpTopo.routerName

	def getMidL2RInterface(self, id):
		return self.getMidLeftName(id) + "-eth2"

	def getMidR2LInterface(self, id):
		return self.getMidRightName(id) + "-eth" + str(id)
