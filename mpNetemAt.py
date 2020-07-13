class MpNetemAt:
	def __init__(self, at, cmd):
		self.at = at
		self.cmd = cmd
		self.delta = 0

	def __str__(self):
		return "Netem... at " + str(self.at) + "(" + str(self.delta) + \
				") will be " + self.cmd
