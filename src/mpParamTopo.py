from mpLinkCharacteristics import MpLinkCharacteristics


class MpParamTopo:
	LSUBNET = "leftSubnet"
	RSUBNET = "rightSubnet"
	defaultValue = {}
	defaultValue[LSUBNET] = "10.1."
	defaultValue[RSUBNET] = "10.2."

	def __init__(self, paramFile):
		self.paramDic = {}
		self.linkCharacteristics = []
		print("Create the param Object")
		self.loadParamFile(paramFile)
		self.loadLinkCharacteristics()
	
	def loadParamFile(self, paramFile):
		f = open(paramFile)
		i = 0
		for l in f:
			i = i + 1
			if l.startswith("#"):
				continue

			tab = l.split(":")
			if len(tab) == 2:
				self.paramDic[tab[0]] = tab[1][:-1]
			else:
				print("Ignored Line " + str(i))
				print(l),
				print("In file " + paramFile)
		f.close()

	def loadLinkCharacteristics(self):
		i = 0 
		for k in sorted(self.paramDic):
			if k.startswith("path"):
				tab = self.paramDic[k].split(",")
				if len(tab) == 3:
					i = i + 1
					path = MpLinkCharacteristics(i,tab[0],
							tab[1], tab[2])
					self.linkCharacteristics.append(path)
				else:
					print("Ignored path :")
					print(self.paramDic[k])

	def getParam(self, key):
		if key in self.paramDic:
			return self.paramDic[key]
		elif key in MpParamTopo.defaultValue:
			return MpParamTopo[key]
		else:
			raise Exception("Param not found " + key)

	def __str__(self):
		s = self.paramDic.__str__()
		s = s + "\n"
		for p in self.linkCharacteristics[:-1]:
			s = s + p.__str__() + "\n"
		s = s + self.linkCharacteristics[-1].__str__()
		return s
