from core.experience import Experience, ExperienceParameter, ExperienceParameter
from core.topo import Topo, TopoParameter

from mininet_builder import MininetBuilder

from mpMultiInterfaceTopo import MpMultiInterfaceTopo
from mpMultiInterfaceConfig import MpMultiInterfaceConfig
from mpMultiInterfaceCongConfig import MpMultiInterfaceCongConfig
from mpMultiInterfaceCongTopo import MpMultiInterfaceCongTopo
from mpECMPSingleInterfaceConfig import MpECMPSingleInterfaceConfig
from mpTwoInterfaceCongestionConfig import MpTwoInterfaceCongestionConfig
from mpExperiencePing import ExperiencePing
from mpExperienceNCPV import ExperienceNCPV
from mpExperienceNC import ExperienceNC
from mpExperienceHTTPS import ExperienceHTTPS
from mpExperienceHTTP import ExperienceHTTP
from mpExperienceSendFile import ExperienceSendFile
from mpExperienceEpload import ExperienceEpload
from mpExperienceNetperf import ExperienceNetperf
from mpExperienceAb import ExperienceAb
from mpExperienceSiri import ExperienceSiri
from mpExperienceVLC import ExperienceVLC
from mpExperienceIperf import ExperienceIperf
from mpExperienceDITG import ExperienceDITG
from mpExperienceMsg import ExperienceMsg
from mpExperienceSiriHTTP import ExperienceSiriHTTP
from mpExperienceSiriMsg import ExperienceSiriMsg
from mpExperienceQUIC import ExperienceQUIC
from mpExperienceQUICSiri import ExperienceQUICSiri
from mpExperienceNone import ExperienceNone
from mpECMPSingleInterfaceTopo import MpECMPSingleInterfaceTopo
from mpTwoInterfaceCongestionTopo import MpTwoInterfaceCongestionTopo

class MpXpRunner:
	def __init__(self, builderType, topoParamFile, xpParamFile):
		self.defParamXp(xpParamFile)
		self.topoParam = TopoParameter(topoParamFile)
		self.defBuilder(builderType)
		self.defTopo()
		self.defConfig()
		self.startTopo()
		self.runXp()
		self.stopTopo()

	def defParamXp(self, xpParamFile):
		self.xpParam = ExperienceParameter(xpParamFile)

	def defBuilder(self, builderType):
		if builderType == Topo.mininetBuilder:
			self.topoBuilder = MininetBuilder()
		else:
			raise Exception("I can not find the builder " +
					builderType)
	def defTopo(self):
		t = self.topoParam.getParam(Topo.topoAttr)
		if t == Topo.multiIfTopo:
			self.Topo = MpMultiInterfaceTopo(self.topoBuilder,
					self.topoParam)
		elif t == Topo.ECMPLikeTopo:
			self.Topo = MpECMPSingleInterfaceTopo(
					self.topoBuilder,
					self.topoParam)
		elif t == Topo.twoIfCongTopo:
			self.Topo = MpTwoInterfaceCongestionTopo(
					self.topoBuilder, self.topoParam)
		elif t == Topo.multiIfCongTopo:
			self.Topo = MpMultiInterfaceCongTopo(self.topoBuilder,
					self.topoParam)
		else:
			raise Exception("Unfound Topo" + t)
		print(self.Topo)

	def defConfig(self):
		t = self.topoParam.getParam(Topo.topoAttr)
		if t == Topo.multiIfTopo:
			self.TopoConfig = MpMultiInterfaceConfig(self.Topo,
				self.topoParam)
		elif t == Topo.ECMPLikeTopo:
			self.TopoConfig = MpECMPSingleInterfaceConfig(
					self.Topo,
					self.topoParam)
		elif t == Topo.twoIfCongTopo:
			self.TopoConfig = MpTwoInterfaceCongestionConfig(
					self.Topo, self.topoParam)
		elif t == Topo.multiIfCongTopo:
			self.TopoConfig = MpMultiInterfaceCongConfig(self.Topo,
				self.topoParam)
		else:
			raise Exception("Unfound Topo" + t)

	def startTopo(self):
		self.Topo.startNetwork()
		self.TopoConfig.configureNetwork()

	def runXp(self):
		xp = self.xpParam.getParam(ExperienceParameter.XPTYPE)
		if xp ==Experience.PING:
			ExperiencePing(self.xpParam, self.Topo,
					self.TopoConfig)
		elif xp ==Experience.NCPV:
			ExperienceNCPV(self.xpParam, self.Topo,
					self.TopoConfig)
		elif xp ==Experience.NC:
			ExperienceNC(self.xpParam, self.Topo,
					self.TopoConfig)
		elif xp ==Experience.NONE:
			ExperienceNone(self.xpParam, self.Topo,
					self.TopoConfig)
		elif xp ==Experience.HTTPS:
			ExperienceHTTPS(self.xpParam, self.Topo,
					self.TopoConfig)
		elif xp ==Experience.HTTP:
			ExperienceHTTP(self.xpParam, self.Topo,
					self.TopoConfig)
		elif xp ==Experience.EPLOAD:
			ExperienceEpload(self.xpParam, self.Topo,
					self.TopoConfig)
		elif xp ==Experience.NETPERF:
			ExperienceNetperf(self.xpParam, self.Topo,
					self.TopoConfig)
		elif xp ==Experience.AB:
			ExperienceAb(self.xpParam, self.Topo,
					self.TopoConfig)
		elif xp ==Experience.SIRI:
			ExperienceSiri(self.xpParam, self.Topo,
					self.TopoConfig)
		elif xp ==Experience.SENDFILE:
			ExperienceSendFile(self.xpParam, self.Topo,
					self.TopoConfig)
		elif xp ==Experience.VLC:
			ExperienceVLC(self.xpParam, self.Topo,
					self.TopoConfig)
		elif xp ==Experience.IPERF:
			ExperienceIperf(self.xpParam, self.Topo,
					self.TopoConfig)
		elif xp ==Experience.DITG:
			ExperienceDITG(self.xpParam, self.Topo, self.TopoConfig)
		elif xp ==Experience.MSG:
			ExperienceMsg(self.xpParam, self.Topo, self.TopoConfig)
		elif xp ==Experience.SIRIHTTP:
			ExperienceSiriHTTP(self.xpParam, self.Topo, self.TopoConfig)
		elif xp ==Experience.SIRIMSG:
			ExperienceSiriMsg(self.xpParam, self.Topo, self.TopoConfig)
		elif xp ==Experience.QUIC:
			ExperienceQUIC(self.xpParam, self.Topo, self.TopoConfig)
		elif xp ==Experience.QUICSIRI:
			ExperienceQUICSiri(self.xpParam, self.Topo, self.TopoConfig)
		else:
			print("Unfound xp type..." + xp)

	def stopTopo(self):
		self.Topo.stopNetwork()
