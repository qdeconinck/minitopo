from mpConfig import MpConfig
from mpECMPSingleInterfaceTopo import MpECMPSingleInterfaceTopo
from mpParamTopo import MpParamTopo
from mpTopo import MpTopo
from struct import *

class MpECMPSingleInterfaceConfig(MpConfig):
	def __init__(self, topo, param):
		MpConfig.__init__(self, topo, param)

	def configureNetwork(self):
		self.configureInterfaces()
		self.configureRoute()
	
	def configureRoute(self):
		i = 0
		for l in self.topo.routers:
			##todo calculate mask length
			cmd = self.getIptableRuleICMP(3, i)
			self.topo.commandTo(self.client, cmd)
			self.topo.commandTo(self.server, cmd)

			cmd = self.getIpRuleCmd(i)
			self.topo.commandTo(self.client, cmd)
			self.topo.commandTo(self.server, cmd)
			
			cmd = self.getDefaultRouteCmd(self.getRouterIPClient(i),
					i)
			self.topo.commandTo(self.client, cmd)
			cmd = self.getDefaultRouteCmd(self.getRouterIPServer(i),
					i)
			self.topo.commandTo(self.server, cmd)
			
			i = i + 1
		
		###
		cmd = self.addRouteDefaultSimple(self.getRouterIPServer(0))
		self.topo.commandTo(self.server, cmd)
		
		cmd = self.addRouteDefaultSimple(self.getRouterIPClient(0))
		self.topo.commandTo(self.client, cmd)
		
		self.topo.commandTo(self.client, "ip route flush cache")
		self.topo.commandTo(self.server, "ip route flush cache")

	def getIptableRuleICMP(self, maskLen, id):
		s = 'iptables -t mangle -A OUTPUT -m u32 --u32 ' + \
				'"6&0xFF=0x1 && ' + \
				'24&0x' + \
				pack('>I',(maskLen)).encode('hex') + \
				'=0x' + pack('>I',id).encode('hex') + \
				'" -j MARK --set-mark ' + str(id + 1)
		print (s)
		return s

	
	def getIpRuleCmd(self, id):
		s = 'ip rule add fwmark ' + str(id + 1) + ' table ' + \
				str(id + 1)
		print(s)
		return s

	def getDefaultRouteCmd(self, via, id):
		s = 'ip route add default via ' + via + ' table ' + str(id + 1)
		print(s)
		return s

	def configureInterfaces(self):
		self.client = self.topo.getHost(MpTopo.clientName)
		self.server = self.topo.getHost(MpTopo.serverName)
		self.routers = []
		i = 0
		netmask = "255.255.255.0"
		for l in self.topo.routers:
			self.routers.append(self.topo.getHost(
				MpTopo.routerNamePrefix + str(i)))
			cmd = self.interfaceUpCommand(
					self.getRouterInterfaceLSwitch(i),
					self.getRouterIPClient(i), netmask)
			self.topo.commandTo(self.routers[-1] , cmd)
			
			cmd = self.interfaceUpCommand(
					self.getRouterInterfaceRSwitch(i),
					self.getRouterIPServer(i), netmask)
			self.topo.commandTo(self.routers[-1] , cmd)

			i = i + 1

		cmd = self.interfaceUpCommand(self.getClientInterface(0),
				self.getClientIP(0), netmask)
		self.topo.commandTo(self.client, cmd)
		
		cmd = self.interfaceUpCommand(self.getServerInterface(),
				self.getServerIP(), netmask)
		self.topo.commandTo(self.server, cmd)

	def getClientIP(self, interfaceID):
		lSubnet = self.param.getParam(MpParamTopo.LSUBNET)
		clientIP = lSubnet + str(interfaceID) + ".1"
		return clientIP

	def getClientSubnet(self, interfaceID):
		lSubnet = self.param.getParam(MpParamTopo.LSUBNET)
		clientSubnet = lSubnet + str(interfaceID) + ".0/24"
		return clientSubnet

	def getRouterIPClient(self, id):
		lSubnet = self.param.getParam(MpParamTopo.LSUBNET)
		routerIP = lSubnet + "0." + str(id + 2)
		return routerIP

	def getRouterIPServer(self, id):
		rSubnet = self.param.getParam(MpParamTopo.RSUBNET)
		routerIP = rSubnet + "0." + str(id + 2)
		return routerIP
	
	def getServerIP(self):
		rSubnet = self.param.getParam(MpParamTopo.RSUBNET)
		serverIP = rSubnet + "0.1"
		return serverIP

	def getClientInterfaceCount(self):
		return 1

	def getRouterInterfaceLSwitch(self, id):
		return  MpTopo.routerNamePrefix + str(id) + "-eth0"

	def getRouterInterfaceRSwitch(self, id):
		return  MpTopo.routerNamePrefix + str(id) + "-eth1"

	def getClientInterface(self, interfaceID):
		return  MpTopo.clientName + "-eth" + str(interfaceID)
	
	def getServerInterface(self):
		return  MpTopo.serverName + "-eth0"

