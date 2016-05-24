class MpConfig:

	PING_OUTPUT = "ping.log"

	def __init__(self, topo, param):
		self.topo = topo
		self.param = param

	def configureNetwork(self):
		print("Configure interfaces....Generic call ?")
		self.configureInterfaces()
		self.configureRoute()

	def getMidL2RInterface(self, id):
		"get Middle link, left to right interface"
		pass

	def getMidR2LInterface(self, id):
		pass

	def getMidLeftName(self, i):
		"get Middle link, left box name"
		pass

	def getMidRightName(self, i):
		pass

	def configureInterfaces(self):
		pass

	def getClientInterfaceCount(self):
		raise Exception("To be implemented")

	def interfaceBUPCommand(self, interfaceName):
		s = "/home/mininet/git/iproute-mptcp/ip/ip link set dev " + interfaceName + " multipath backup "
		print(s)
		return s

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

	def arpCommand(self, ip, mac):
		s = "arp -s " + ip + " " + mac
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
