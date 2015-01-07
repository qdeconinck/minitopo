


class MpLinkCharacteristics:
	def __init__(self, id, delay, queueSize, bandwidth):
		self.id = id
		self.delay = delay
		self.queueSize = queueSize
		self.bandwidth = bandwidth
	
	def asDict(self):
		d = {}
		d['delay'] = self.delay
		d['queueSize'] = self.queueSize
		d['bandwidth'] = self.bandwidth
		return d

	def __str__(self):
		s = "Link id : " + str(self.id) + "\n"
		s =  s + "\tDelay : " + str(self.delay) + "\n"
		s =  s + "\tQueue Size : " + str(self.queueSize) + "\n"
		s =  s + "\tBandwidth : " + str(self.bandwidth)
		return s
		
