from mpTopo import MpTopo
from mpParamTopo import MpParamTopo
from mpParamXp import MpParamXp
from mpMultiInterfaceTopo import MpMultiInterfaceTopo
from mpMultiInterfaceConfig import MpMultiInterfaceConfig
from mpECMPSingleInterfaceConfig import MpECMPSingleInterfaceConfig
from mpTwoInterfaceCongestionConfig import MpTwoInterfaceCongestionConfig
from mpMininetBuilder import MpMininetBuilder
from mpExperiencePing import MpExperiencePing
from mpExperienceNCPV import MpExperienceNCPV
from mpExperienceNC import MpExperienceNC
from mpExperienceHTTPS import MpExperienceHTTPS
from mpExperienceHTTP import MpExperienceHTTP
from mpExperienceSendFile import MpExperienceSendFile
from mpExperienceEpload import MpExperienceEpload
from mpExperienceNetperf import MpExperienceNetperf
from mpExperienceAb import MpExperienceAb
from mpExperienceSiri import MpExperienceSiri
from mpExperienceVLC import MpExperienceVLC
from mpExperienceIperf import MpExperienceIperf
from mpExperienceDITG import MpExperienceDITG
from mpExperienceMsg import MpExperienceMsg
from mpExperienceSiriHTTP import MpExperienceSiriHTTP
from mpExperienceSiriMsg import MpExperienceSiriMsg
from mpExperienceQUIC import MpExperienceQUIC
from mpExperienceNone import MpExperienceNone
from mpExperience import MpExperience
from mpECMPSingleInterfaceTopo import MpECMPSingleInterfaceTopo
from mpTwoInterfaceCongestionTopo import MpTwoInterfaceCongestionTopo

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
		elif t == MpTopo.twoIfCongTopo:
			self.mpTopo = MpTwoInterfaceCongestionTopo(
					self.topoBuilder, self.topoParam)
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
		elif t == MpTopo.twoIfCongTopo:
			self.mpTopoConfig = MpTwoInterfaceCongestionConfig(
					self.mpTopo, self.topoParam)
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
		elif xp == MpExperience.NCPV:
			MpExperienceNCPV(self.xpParam, self.mpTopo,
					self.mpTopoConfig)
		elif xp == MpExperience.NC:
			MpExperienceNC(self.xpParam, self.mpTopo,
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
		elif xp == MpExperience.EPLOAD:
			MpExperienceEpload(self.xpParam, self.mpTopo,
					self.mpTopoConfig)
		elif xp == MpExperience.NETPERF:
			MpExperienceNetperf(self.xpParam, self.mpTopo,
					self.mpTopoConfig)
		elif xp == MpExperience.AB:
			MpExperienceAb(self.xpParam, self.mpTopo,
					self.mpTopoConfig)
		elif xp == MpExperience.SIRI:
			MpExperienceSiri(self.xpParam, self.mpTopo,
					self.mpTopoConfig)
		elif xp == MpExperience.SENDFILE:
			MpExperienceSendFile(self.xpParam, self.mpTopo,
					self.mpTopoConfig)
		elif xp == MpExperience.VLC:
			MpExperienceVLC(self.xpParam, self.mpTopo,
					self.mpTopoConfig)
		elif xp == MpExperience.IPERF:
			MpExperienceIperf(self.xpParam, self.mpTopo,
					self.mpTopoConfig)
		elif xp == MpExperience.DITG:
			MpExperienceDITG(self.xpParam, self.mpTopo, self.mpTopoConfig)
		elif xp == MpExperience.MSG:
			MpExperienceMsg(self.xpParam, self.mpTopo, self.mpTopoConfig)
		elif xp == MpExperience.SIRIHTTP:
			MpExperienceSiriHTTP(self.xpParam, self.mpTopo, self.mpTopoConfig)
		elif xp == MpExperience.SIRIMSG:
			MpExperienceSiriMsg(self.xpParam, self.mpTopo, self.mpTopoConfig)
		elif xp == MpExperience.QUIC:
			MpExperienceQUIC(self.xpParam, self.mpTopo, self.mpTopoConfig)
		else:
			print("Unfound xp type..." + xp)

	def stopTopo(self):
		self.mpTopo.stopNetwork()
