class MpTopo:
	"""Simple MpTopo"""
	def __init__(self, topoBuilder, topoParam):
		self.topoBuilder = topoBuilder
		self.topoParam = topoParam 
	
	def commandTo(self, who, cmd):
		pass

	def getHost(self, who):
		pass

	def addHost(self, host):
		print("TODO, add host " + host)
		self.topoBuilder.addHost(host)
		pass

	def addSwitch(self, switch):
		print("TODO, add switchi " + switch)
		self.topoBuilder.addSwitch(switch)
		pass

	def addLink(self, fromA, toB, **kwargs):
		#todo check syntax for **kwargs
		self.topoBuilder.addLink(fromA,toB,**kwargs)
		pass

	
