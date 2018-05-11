from mpTopo import MpTopo
from mpParamTopo import MpParamTopo
from mpParamXp import MpParamXp
from mpMultiInterfaceTopo import MpMultiInterfaceTopo
from mpMultiInterfaceConfig import MpMultiInterfaceConfig
from mpECMPSingleInterfaceConfig import MpECMPSingleInterfaceConfig
from mpMininetBuilder import MpMininetBuilder
from mpExperiencePing import MpExperiencePing
from mpExperienceHTTPS import MpExperienceHTTPS
from mpExperienceHTTP import MpExperienceHTTP
from mpExperienceSiri import MpExperienceSiri
from mpExperienceMsg import MpExperienceMsg
from mpExperienceSiriMsg import MpExperienceSiriMsg
from mpExperienceNone import MpExperienceNone
from mpExperience import MpExperience
from mpECMPSingleInterfaceTopo import MpECMPSingleInterfaceTopo

class MpXpRunner:
	def __init__(self, builderType, topoParamFile, xpParamFile):
		self.defParamXp(xpParamFile)
		self.topoParam = MpParamTopo(topoParamFile)
		self.defBuilder(builderType)
		self.defTopo()
		self.defConfig()
		self.startTopo()
		self.runXp()
		self.stopTopo()

	def defParamXp(self, xpParamFile):
		self.xpParam = MpParamXp(xpParamFile)

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
		elif t == MpTopo.ECMPLikeTopo:
			self.mpTopo = MpECMPSingleInterfaceTopo(
					self.topoBuilder,
					self.topoParam)
		else:
			raise Exception("Unfound Topo" + t)
		print(self.mpTopo)

	def defConfig(self):
		t = self.topoParam.getParam(MpTopo.topoAttr)
		if t == MpTopo.multiIfTopo:
			self.mpTopoConfig = MpMultiInterfaceConfig(self.mpTopo,
				self.topoParam)
		elif t == MpTopo.ECMPLikeTopo:
			self.mpTopoConfig = MpECMPSingleInterfaceConfig(
					self.mpTopo,
					self.topoParam)
		else:
			raise Exception("Unfound Topo" + t)

	def startTopo(self):
		self.mpTopo.startNetwork()
		self.mpTopoConfig.configureNetwork()

	def runXp(self):
		xp = self.xpParam.getParam(MpParamXp.XPTYPE)
		if xp == MpExperience.PING:
			MpExperiencePing(self.xpParam, self.mpTopo,
					self.mpTopoConfig)
		elif xp == MpExperience.NONE:
			MpExperienceNone(self.xpParam, self.mpTopo,
					self.mpTopoConfig)
		elif xp == MpExperience.HTTPS:
			MpExperienceHTTPS(self.xpParam, self.mpTopo,
					self.mpTopoConfig)
		elif xp == MpExperience.HTTP:
			MpExperienceHTTP(self.xpParam, self.mpTopo,
					self.mpTopoConfig)
		elif xp == MpExperience.SIRI:
			MpExperienceSiri(self.xpParam, self.mpTopo,
					self.mpTopoConfig)
		elif xp == MpExperience.MSG:
			MpExperienceMsg(self.xpParam, self.mpTopo, self.mpTopoConfig)
		elif xp == MpExperience.SIRIMSG:
			MpExperienceSiriMsg(self.xpParam, self.mpTopo, self.mpTopoConfig)
		else:
			print("Unfound xp type..." + xp)

	def stopTopo(self):
		self.mpTopo.stopNetwork()
