


class MpLinkCharacteristics:
	def __init__(self, id, delay, queueSize, bandwidth):
		self.id = id
		self.delay = delay
		self.queueSize = queueSize
		self.bandwidth = bandwidth
		self.netemAt = []

	def addNetemAt(self, n):
		if len(self.netemAt) == 0:
			n.delay = n.at
			self.netemAt.append(n)
		else:
			if n.at > self.netemAt[-1].at:
				n.delta = n.at - self.netemAt[-1].at
				self.netemAt.append(n)
			else:
				print("Do not take into account " + n.__str__() + \
						"because ooo !")
			pass
	
	def buildNetemCmd(self):
		cmd = ""
		for n in self.netemAt:
			cmd = cmd + "sleep " + str(n.delta)
			cmd = cmd + " && "
			cmd = cmd + " echo " + n.cmd + " && "
		cmd = cmd + " true &"

	def asDict(self):
		d = {}
		d['bw'] = int(self.bandwidth)
		d['delay'] = self.delay + "ms"
		d['max_queue_size'] = int(self.queueSize)
		return d

	def __str__(self):
		s = "Link id : " + str(self.id) + "\n"
		s =  s + "\tDelay : " + str(self.delay) + "\n"
		s =  s + "\tQueue Size : " + str(self.queueSize) + "\n"
		s =  s + "\tBandwidth : " + str(self.bandwidth) + "\n"
		for l in self.netemAt:
			s = s + "\t" + l.__str__() + "\n"
		return s
		
