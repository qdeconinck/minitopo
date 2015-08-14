from mpParam import MpParam

class MpParamXp(MpParam):

	RMEM       = "rmem"
	WMEM       = "wmem"
	SCHED      = "sched"
	KERNELPM   = "kpm"
	KERNELPMC  = "kpmc" #kernel path manager client / server
	KERNELPMS  = "kpms"
	USERPMC	   = "upmc"
	USERPMS	   = "upms" #userspace path manager client / server
	USERPMCARGS   = "upmc_args"
	USERPMSARGS   = "upms_args"
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
	CHANGEPV   = "changePv"
	CHANGEPVAT = "changePvAt"
	HTTPSFILE  = "file" # file to wget, if random : we create a file with random data called random.
	HTTPSRANDOMSIZE = "file_size" # if file is set to random, define the size of the random file


	# global sysctl
	sysctlKey = {}
	sysctlKey[RMEM] = "net.ipv4.tcp_rmem"
	sysctlKey[WMEM] = "net.ipv4.tcp_wmem"
	sysctlKey[KERNELPM] = "net.mptcp.mptcp_path_manager"
	sysctlKey[SCHED] = "net.mptcp.mptcp_scheduler"

	sysctlKeyClient = {}
	sysctlKeyClient[KERNELPMC] = "net.mptcp.mptcp_path_manager"
	sysctlKeyServer = {}
	sysctlKeyServer[KERNELPMS] = "net.mptcp.mptcp_path_manager"

	defaultValue = {}

	defaultValue[RMEM] = "10240 87380 16777216"
	defaultValue[WMEM] = "4096 16384 4194304"
	defaultValue[KERNELPM] = "fullmesh"
	defaultValue[KERNELPMC] = "fullmesh"
	defaultValue[KERNELPMS] = "fullmesh"
	defaultValue[USERPMC] = "fullmesh"
	defaultValue[USERPMS] = "fullmesh"
	defaultValue[USERPMCARGS] = ""
	defaultValue[USERPMSARGS] = ""
	defaultValue[SCHED] = "default"

	defaultValue[CLIENTPCAP] = "no"
	defaultValue[SERVERPCAP] = "no"
	defaultValue[XPTYPE] = "none"
	defaultValue[PINGCOUNT] = "5"
	defaultValue[DDIBS] = "1k"
	defaultValue[DDOBS] = "1k"
	defaultValue[DDCOUNT] = "5000" #5k * 1k = 5m
	defaultValue[PVRATELIMIT] = "400k"
	defaultValue[PVZ] = "10000"
	defaultValue[PVG] = "10000"
	defaultValue[NCSERVERPORT] = "33666"
	defaultValue[NCCLIENTPORT] = "33555"
	defaultValue[CHANGEPV] = "no"
	defaultValue[HTTPSFILE] = "random"
	defaultValue[HTTPSRANDOMSIZE] = "1024"

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
