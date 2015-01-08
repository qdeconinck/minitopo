from mpTopo import MpTopo
from mpParamTopo import MpParamTopo
from mpMultiInterfaceTopo import MpMultiInterfaceTopo
from mpMultiInterfaceConfig import MpMultiInterfaceConfig
from mpMininetBuilder import MpMininetBuilder

class MpXpRunner:
	def __init__(self, builderType, topoParamFile, xpParamFile):
		self.topoParam = MpParamTopo(topoParamFile)
		self.defBuilder(builderType)
		self.defTopo()
		self.defConfig()
		self.startTopo()
		self.runXp(xpParamFile)
		self.stopTopo()
		
	def defBuilder(self, builderType):
		if builderType == MpTopo.mininetBuilder:
			self.topoBuilder = MpMininetBuilder()
		else:
			raise Exception("I can not find the builder " + 
					builderType)
	def defTopo(self):
		t = self.topoParam.getParam(MpTopo.topoAttr)
		if t == MpTopo.multiIfTopo:
			self.mpTopo = MpMultiInterfaceTopo(self.topoBuilder,
					self.topoParam)
		else:
			raise Exception("Unfound Topo" + t)
		print(self.mpTopo)

	def defConfig(self):
		self.mpTopoConfig = MpMultiInterfaceConfig(self.mpTopo,
				self.topoParam)

	def startTopo(self):
		self.mpTopo.startNetwork()
		self.mpTopoConfig.configureNetwork()

	def runXp(self, xpParamFile):
		if xpParamFile is None:
			self.mpTopoConfig.pingAllFromClient()
			self.mpTopo.getCLI()
		else:
			raise Exception("TODO")
	
	def stopTopo(self):
		self.mpTopo.stopNetwork()
