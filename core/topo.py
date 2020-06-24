from .parameter import Parameter

from mpLinkCharacteristics import MpLinkCharacteristics
from mpNetemAt import MpNetemAt

class TopoParameter(Parameter):
	LSUBNET = "leftSubnet"
	RSUBNET = "rightSubnet"
	netemAt = "netemAt_"
	changeNetem = "changeNetem"
	defaultValue = {}
	defaultValue[LSUBNET] = "10.1."
	defaultValue[RSUBNET] = "10.2."
	defaultValue[changeNetem] = "false"

	def __init__(self, paramFile):
		Parameter.__init__(self, paramFile)
		self.linkCharacteristics = []
		self.loadLinkCharacteristics()
		self.loadNetemAt()
		print(self.__str__())

	def loadNetemAt(self):
		if not self.getParam(TopoParameter.changeNetem) == "yes":
			return
		for k in sorted(self.paramDic):
			if k.startswith(TopoParameter.netemAt):
				i = int(k[len(TopoParameter.netemAt):])
				val = self.paramDic[k]
				if not isinstance(val, list):
					tmp = val
					val = []
					val.append(tmp)
				self.loadNetemAtList(i, val)

	def loadNetemAtList(self, id, nlist):
		for n in nlist:
			tab = n.split(",")
			if len(tab)==2:
				o = MpNetemAt(float(tab[0]), tab[1])
				if id < len(self.linkCharacteristics):
					self.linkCharacteristics[id].addNetemAt(o)
				else:
					print("Error can't set netem for link " + str(id))
			else:
				print("Netem wrong line : " + n)
		print(self.linkCharacteristics[id].netemAt)

	def loadLinkCharacteristics(self):
		i = 0
		for k in sorted(self.paramDic):
			if k.startswith("path"):
				tab = self.paramDic[k].split(",")
				bup = False
				loss = "0.0"
				if len(tab) == 5:
					loss = tab[3]
					bup = tab[4] == 'True'
				if len(tab) == 4:
					try:
						loss = float(tab[3])
						loss = tab[3]
					except ValueError:
						bup = tab[3] == 'True'
				if len(tab) == 3 or len(tab) == 4 or len(tab) == 5:
					path = MpLinkCharacteristics(i,tab[0],
							tab[1], tab[2], loss, bup)
					self.linkCharacteristics.append(path)
					i = i + 1
				else:
					print("Ignored path :")
					print(self.paramDic[k])

	def getParam(self, key):
		val = Parameter.getParam(self, key)
		if val is None:
			if key in TopoParameter.defaultValue:
				return TopoParameter.defaultValue[key]
			else:
				raise Exception("Param not found " + key)
		else:
			return val

	def __str__(self):
		s = Parameter.__str__(self)
		s = s + "\n"
		for p in self.linkCharacteristics[:-1]:
			s = s + p.__str__() + "\n"
		s = s + self.linkCharacteristics[-1].__str__()
		return s

class Topo:
	mininetBuilder = "mininet"
	multiIfTopo = "MultiIf"
	ECMPLikeTopo = "ECMPLike"
	twoIfCongTopo = "twoIfCong"
	multiIfCongTopo = "MultiIfCong"
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
		self.changeNetem = topoParam.getParam(TopoParameter.changeNetem)
		self.logFile = open(Topo.cmdLog, 'w')

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


class TopoConfig:

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
                " >> " + TopoConfig.PING_OUTPUT
        print(s)
        return s
