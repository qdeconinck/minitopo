class MpConfig:
	
	PING_OUTPUT = "ping.log"

	def __init__(self, topo, param):
		self.topo = topo
		self.param = param

	def getClientInterfaceCount(self):
		raise Exception("To be implemented")

	def interfaceUpCommand(self, interfaceName, ip, subnet):
		s = "ifconfig " + interfaceName + " " + ip + " netmask " + \
			subnet
		print(s)
		return s

	def addRouteTableCommand(self, fromIP, id):
		s = "ip rule add from " + fromIP + " table " + str(id + 1)
		print(s)
		return s

	def addRouteScopeLinkCommand(self, network, interfaceName, id):
		s = "ip route add " + network + " dev " + interfaceName + \
				" scope link table " + str(id + 1)
		print(s)
		return s

	def addRouteDefaultCommand(self, via, id):
		s = "ip route add default via " + via + " table " + str(id + 1)
		print(s)
		return s

	def addRouteDefaultGlobalCommand(self, via, interfaceName):
		s = "ip route add default scope global nexthop via " + via + \
				" dev " + interfaceName
		print(s)
		return s

	def addRouteDefaultSimple(self, via):
		s = "ip route add default via " + via
		print(s)
		return s
	
	def pingCommand(self, fromIP, toIP, n=5):
		s = "ping -c " + str(n) + " -I " + fromIP + " " + toIP + \
				" >> " + MpConfig.PING_OUTPUT
		print(s)
		return s
