


class MpLinkCharacteristics:

	tcNetemParent = "5:1"
	tcNetemHandle = "10:"

	def __init__(self, id, delay, queueSize, bandwidth, loss, back_up=False):
		self.id = id
		self.delay = delay
		self.queueSize = queueSize
		self.bandwidth = bandwidth
		self.loss = loss
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

	def buildNetemCmd(self, ifname):
		cmd = ""
		for n in self.netemAt:
			cmd = cmd + "sleep " + str(n.delta)
			cmd = cmd + " && "
			cmd = cmd + " tc qdisc change dev " + ifname + " "
			cmd = cmd + " parent " + MpLinkCharacteristics.tcNetemParent
			cmd = cmd + " handle " + MpLinkCharacteristics.tcNetemHandle
			cmd = cmd + " netem " + n.cmd + "delay " + self.delay
			cmd = cmd + " rate " + self.bandwidth + "mbit && "
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
