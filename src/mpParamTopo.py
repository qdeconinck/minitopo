from mpLinkCharacteristics import MpLinkCharacteristics
from mpParam import MpParam
from mpNetemAt import MpNetemAt

class MpParamTopo(MpParam):
	LSUBNET = "leftSubnet"
	RSUBNET = "rightSubnet"
	netemAt = "netemAt_"
	changeNetem = "changeNetem"
	defaultValue = {}
	defaultValue[LSUBNET] = "10.1."
	defaultValue[RSUBNET] = "10.2."
	defaultValue[changeNetem] = "false"

	def __init__(self, paramFile):
		MpParam.__init__(self, paramFile)
		self.linkCharacteristics = []
		self.loadLinkCharacteristics()
		self.loadNetemAt()
		print(self.__str__())

	def loadNetemAt(self):
		if not self.getParam(MpParamTopo.changeNetem) == "yes":
			return
		for k in sorted(self.paramDic):
			if k.startswith(MpParamTopo.netemAt):
				i = int(k[len(MpParamTopo.netemAt):])
				val = self.paramDic[k]
				if not isinstance(val, list):
					tmp = val
					val = []
					val.append(tmp)
				self.loadNetemAtList(i, val)

	def loadNetemAtList(self, id, nlist):
		for n in nlist:
			tab = n.split(",")
			if len(tab)==2:
				o = MpNetemAt(float(tab[0]), tab[1])
				if id < len(self.linkCharacteristics):
					self.linkCharacteristics[id].addNetemAt(o)
				else:
					print("Error can't set netem for link " + str(id))
			else:
				print("Netem wrong line : " + n)
		print(self.linkCharacteristics[id].netemAt)

	def loadLinkCharacteristics(self):
		i = 0
		for k in sorted(self.paramDic):
			if k.startswith("path"):
				tab = self.paramDic[k].split(",")
				bup = False
				loss = "0.0"
				if len(tab) == 5:
					loss = tab[3]
					bup = tab[4] == 'True'
				if len(tab) == 4:
					try:
						loss = float(tab[3])
						loss = tab[3]
					except ValueError:
						bup = tab[3] == 'True'
				if len(tab) == 3 or len(tab) == 4 or len(tab) == 5:
					path = MpLinkCharacteristics(i,tab[0],
							tab[1], tab[2], loss, bup)
					self.linkCharacteristics.append(path)
					i = i + 1
				else:
					print("Ignored path :")
					print(self.paramDic[k])

	def getParam(self, key):
		val = MpParam.getParam(self, key)
		if val is None:
			if key in MpParamTopo.defaultValue:
				return MpParamTopo.defaultValue[key]
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
