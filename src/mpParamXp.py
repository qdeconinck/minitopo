from mpParam import MpParam

class MpParamXp(MpParam):

	RMEM       = "rmem"
	CLIENTPCAP = "clientPcap"
	SERVERPCAP = "serverPcap"
	XPTYPE     = "xpType"
	PINGCOUNT  = "pingCount"

	defaultValue = {}

	defaultValue[RMEM] = "x y z"
	defaultValue[CLIENTPCAP] = "no"
	defaultValue[SERVERPCAP] = "no"
	defaultValue[XPTYPE] = "ping"
	defaultValue[PINGCOUNT] = "5"

	def __init__(self, paramFile):
		MpParam.__init__(self, paramFile)
	
	def getParam(self, key):
		val = MpParam.getParam(self, key)
		if val is None:
			if key in MpParamXp.defaultValue:
				return MpParamXp.defaultValue[key]
			else:
				raise Exception("Param not found " + key)
		else:
			return val

	def __str__(self):
		s = MpParam.__str__(self)
		return s
