from .parameter import Parameter

import math


class NetemAt(object):
    def __init__(self, at, cmd):
        self.at = at
        self.cmd = cmd
        self.delta = 0

    def __str__(self):
        return "Netem... at " + str(self.at) + "(" + str(self.delta) + \
                ") will be " + self.cmd


class LinkCharacteristics(object):
    tcNetemParent = "1:1"
    tcHtbClassid = "10"
    tcNetemHandle = "1:10"

    def bandwidthDelayProductDividedByMTU(self):
        rtt = 2 * float(self.delay)
        """ Since bandwidth is in Mbps and rtt in ms """
        bandwidthDelayProduct = (float(self.bandwidth) * 125000.0) * (rtt / 1000.0)
        return int(math.ceil(bandwidthDelayProduct * 1.0 / 1500.0))

    def bufferSize(self):
        return (1500.0 * self.bandwidthDelayProductDividedByMTU()) + (float(self.bandwidth) * 1000.0 * float(self.queuingDelay) / 8)

    def extractQueuingDelay(self, queueSize, bandwidth, delay, mtu=1500):
        # rtt = 2 * float(delay)
        # bdp_queue_size = int((float(rtt) * float(bandwidth) * 1024 * 1024) / (int(mtu) * 8 * 1000))
        # if int(queueSize) <= bdp_queue_size:
            # Returning 0 seems to bypass everything, then only limited by CPU.
            # This is not what we want...
        # 	return 1

        # queuingQueueSize = int(queueSize) - bdp_queue_size
        queuingDelay = (int(queueSize) * int(mtu) * 8.0 * 1000.0) / (float(bandwidth) * 1024 * 1024)
        return max(int(queuingDelay), 1)

    def __init__(self, id, delay, queueSize, bandwidth, loss, back_up=False):
        self.id = id
        self.delay = delay
        self.queueSize = queueSize
        self.bandwidth = bandwidth
        self.loss = loss
        self.queuingDelay = str(self.extractQueuingDelay(queueSize, bandwidth, delay))
        self.netemAt = []
        self.back_up = back_up

    def addNetemAt(self, n):
        if len(self.netemAt) == 0:
            n.delta = n.at
            self.netemAt.append(n)
        else:
            if n.at > self.netemAt[-1].at:
                n.delta = n.at - self.netemAt[-1].at
                self.netemAt.append(n)
            else:
                print("Do not take into account " + n.__str__() + \
                        "because ooo !")
            pass

    def buildBwCmd(self, ifname):
        cmd = ""
        for n in self.netemAt:
            cmd = cmd + "sleep {}".format(n.delta)
            cmd = cmd + " && tc qdisc del dev {} root ".format(ifname)
            cmd = cmd + " ; tc qdisc add dev {} root handle 5:0 tbf rate {}mbit burst 15000 limit {} &&".format(ifname, self.bandwidth, int(self.bufferSize()))

        cmd = cmd + " true &"
        return cmd

    def buildNetemCmd(self, ifname):
        cmd = ""
        for n in self.netemAt:
            cmd = cmd + "sleep " + str(n.delta)
            cmd = cmd + " && tc qdisc del dev " + ifname + " root "
            cmd = cmd + " ; tc qdisc add dev {} root handle 10: netem {} delay {}ms limit 50000 &&".format(ifname, n.cmd, self.delay)

        cmd = cmd + " true &"
        return cmd

    def buildPolicingCmd(self, ifname):
        cmd = ""
        for n in self.netemAt:
            cmd = cmd + "sleep {}".format(n.delta)
            cmd = cmd + " && tc qdisc del dev {} ingress".format(ifname)
            cmd = cmd + " ; tc qdisc add dev {} handle ffff: ingress".format(ifname)
            cmd = cmd + " && tc filter add dev {} parent ffff: u32 match u32 0 0 police rate {}mbit burst {} drop && ".format(ifname, self.bandwidth, int(self.bufferSize() * 1.2))

        cmd = cmd + " true &"
        return cmd

    def asDict(self):
        d = {}
        d['bw'] = float(self.bandwidth)
        d['delay'] = self.delay + "ms"
        d['loss'] = float(self.loss)
        d['max_queue_size'] = int(self.queueSize)
        return d

    def __str__(self):
        s = "Link id : " + str(self.id) + "\n"
        s =  s + "\tDelay : " + str(self.delay) + "\n"
        s =  s + "\tQueue Size : " + str(self.queueSize) + "\n"
        s =  s + "\tBandwidth : " + str(self.bandwidth) + "\n"
        s =  s + "\tLoss : " + str(self.loss) + "\n"
        s =  s + "\tBack up : " + str(self.back_up) + "\n"
        for l in self.netemAt:
            s = s + "\t" + l.__str__() + "\n"
        return s


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
                o = NetemAt(float(tab[0]), tab[1])
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
                    path = LinkCharacteristics(i,tab[0],
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

class Topo(object):
    """
    Base class to instantiate a topology.

    This class is not instantiable as it. You must define a child class with the
    `NAME` attribute.
    """
    mininetBuilder = "mininet"
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


class TopoConfig(object):
    """
    Base class to instantiate a topology.

    This class is not instantiable as it. You must define a child class with the
    `NAME` attribute.
    """

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
