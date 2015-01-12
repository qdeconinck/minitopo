from mpLinkCharacteristics import MpLinkCharacteristics
from mpParam import MpParam

class MpParamTopo(MpParam):
	LSUBNET = "leftSubnet"
	RSUBNET = "rightSubnet"
	defaultValue = {}
	defaultValue[LSUBNET] = "10.1."
	defaultValue[RSUBNET] = "10.2."

	def __init__(self, paramFile):
		MpParam.__init__(self, paramFile)
		self.linkCharacteristics = []
		self.loadLinkCharacteristics()
	
	def loadLinkCharacteristics(self):
		i = 0 
		for k in sorted(self.paramDic):
			if k.startswith("path"):
				tab = self.paramDic[k].split(",")
				if len(tab) == 3:
					path = MpLinkCharacteristics(i,tab[0],
							tab[1], tab[2])
					self.linkCharacteristics.append(path)
					i = i + 1
				else:
					print("Ignored path :")
					print(self.paramDic[k])

	def getParam(self, key):
		val = MpParam.getParam(self, key)
		if val is None:
			if key in MpParamTopo.defaultValue:
				return MpParamTopo[key]
			else:
				raise Exception("Param not found " + key)
		else:
			return val

	def __str__(self):
		s = MpParam.__str__(self)
		s = s + "\n"
		for p in self.linkCharacteristics[:-1]:
			s = s + p.__str__() + "\n"
		s = s + self.linkCharacteristics[-1].__str__()
		return s
