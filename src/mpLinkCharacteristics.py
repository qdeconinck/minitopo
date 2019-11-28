import math


class MpLinkCharacteristics:

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
		rtt = 2 * float(delay)
		bdp_queue_size = int((float(rtt) * float(bandwidth) * 1024 * 1024) / (int(mtu) * 8 * 1000))
		if int(queueSize) <= bdp_queue_size:
			# Returning 0 seems to bypass everything, then only limited by CPU.
			# This is not what we want...
			return 1

		queuingQueueSize = int(queueSize) - bdp_queue_size
		queuingDelay = (queuingQueueSize * int(mtu) * 8 * 1000) / (float(bandwidth) * 1024 * 1024)
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
