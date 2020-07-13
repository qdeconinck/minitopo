
class MpParam:
	def __init__(self, paramFile):
		self.paramDic = {}
		print("Create the param Object")
		if paramFile is None:
			print("default param...")
		else:
			self.loadParamFile(paramFile)

	def loadParamFile(self, paramFile):
		f = open(paramFile)
		i = 0
		for l in f:
			i = i + 1
			if l.startswith("#"):
				continue

			tab = l.split(":")
			if len(tab) == 2:
				k = tab[0]
				val = tab[1][:-1]
				if k in self.paramDic:
					if not isinstance(self.paramDic[k], list):
						self.paramDic[k] = [self.paramDic[k]]
					self.paramDic[k].append(val)
				else:
					self.paramDic[k] = val
			else:
				print("Ignored Line " + str(i))
				print(l),
				print("In file " + paramFile)
		f.close()

	def getParam(self, key):
		if key in self.paramDic:
			return self.paramDic[key]
		return None

	def __str__(self):
		s = self.paramDic.__str__()
		return s
