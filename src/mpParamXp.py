from mpParam import MpParam

class MpParamXp(MpParam):

	RMEM       = "rmem"
	SCHED      = "sched"
	KERNELPM   = "kpm"
	CLIENTPCAP = "clientPcap"
	SERVERPCAP = "serverPcap"
	XPTYPE     = "xpType"
	PINGCOUNT  = "pingCount"
	DDIBS      = "ddIBS"
	DDOBS      = "ddIBS"
	DDCOUNT    = "ddCount"
	PVRATELIMIT= "pvRateLimit"
	PVG        = "pvG" #patched version of pv
	PVZ        = "pvZ"
	NCSERVERPORT = "ncServerPort"
	NCCLIENTPORT = "ncClientPort"

	# global sysctl
	sysctlKey = {}
	sysctlKey[RMEM] = "net.ipv4.tcp_rmem"
	sysctlKey[KERNELPM] = "net.mptcp.mptcp_path_manager"
	sysctlKey[SCHED] = "net.mptcp.mptcp_scheduler"

	sysctlListClient = []
	sysctlListServer = []

	defaultValue = {}

	defaultValue[RMEM] = "10240 87380 16777216"
	defaultValue[KERNELPM] = "fullmesh"
	defaultValue[SCHED] = "default"

	defaultValue[CLIENTPCAP] = "no"
	defaultValue[SERVERPCAP] = "no"
	defaultValue[XPTYPE] = "ping"
	defaultValue[PINGCOUNT] = "5"
	defaultValue[DDIBS] = "1k"
	defaultValue[DDOBS] = "1k"
	defaultValue[DDCOUNT] = "5000" #5k * 1k = 5m
	defaultValue[PVRATELIMIT] = "400k"
	defaultValue[PVZ] = "10000"
	defaultValue[PVG] = "10000"
	defaultValue[NCSERVERPORT] = "33666"
	defaultValue[NCCLIENTPORT] = "33555"

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
