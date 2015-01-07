


class MpLinkCharacteristics:
	def __init__(self, id, delay, queueSize, bandwidth):
		self.id = id
		self.delay = delay
		self.queueSize = queueSize
		self.bandwidth = bandwidth
	
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
		s =  s + "\tBandwidth : " + str(self.bandwidth)
		return s
		
