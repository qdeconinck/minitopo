from mpParam import MpParam

class MpParamXp(MpParam):

	RMEM       = "rmem"
	WMEM       = "wmem"
	SCHED      = "sched"
	CC		   = "congctrl"
	AUTOCORK   = "autocork"
	EARLYRETRANS = "earlyRetrans"
	KERNELPM   = "kpm"
	KERNELPMC  = "kpmc" #kernel path manager client / server
	KERNELPMS  = "kpms"
	USERPMC	   = "upmc"
	USERPMS	   = "upms" #userspace path manager client / server
	USERPMCARGS   = "upmc_args"
	USERPMSARGS   = "upms_args"
	CLIENTPCAP = "clientPcap"
	SERVERPCAP = "serverPcap"
	SNAPLENPCAP = "snaplenPcap"
	XPTYPE     = "xpType"
	PINGCOUNT  = "pingCount"
	DDIBS      = "ddIBS"
	DDOBS      = "ddIBS"
	DDCOUNT    = "ddCount"
	HTTPSFILE  = "file" # file to wget, if random : we create a file with random data called random.
	HTTPSRANDOMSIZE = "file_size" # if file is set to random, define the size of the random file
	QUICMULTIPATH = "quicMultipath"
	QUICREQRESRUNTIME = "quicReqresRunTime"
	BUFFERAUTOTUNING = "bufferAutotuning"


	# global sysctl
	sysctlKey = {}
	sysctlKey[RMEM] = "net.ipv4.tcp_rmem"
	sysctlKey[WMEM] = "net.ipv4.tcp_wmem"
	sysctlKey[KERNELPM] = "net.mptcp.mptcp_path_manager"
	sysctlKey[SCHED] = "net.mptcp.mptcp_scheduler"
	sysctlKey[CC] = "net.ipv4.tcp_congestion_control"
	sysctlKey[AUTOCORK] = "net.ipv4.tcp_autocorking"
	sysctlKey[EARLYRETRANS] = "net.ipv4.tcp_early_retrans"
	sysctlKey[BUFFERAUTOTUNING] = "net.ipv4.tcp_moderate_rcvbuf"


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
	defaultValue[CC] = "olia"
	defaultValue[SCHED] = "default"
	defaultValue[AUTOCORK] = "1"
	defaultValue[EARLYRETRANS] = "3"
	defaultValue[BUFFERAUTOTUNING] = "1"

	defaultValue[CLIENTPCAP] = "no"
	defaultValue[SERVERPCAP] = "no"
	defaultValue[SNAPLENPCAP] = "65535"  # Default snapping value of tcpdump
	defaultValue[XPTYPE] = "none"
	defaultValue[PINGCOUNT] = "5"
	defaultValue[DDIBS] = "1k"
	defaultValue[DDOBS] = "1k"
	defaultValue[DDCOUNT] = "5000" #5k * 1k = 5m
	defaultValue[HTTPSFILE] = "random"
	defaultValue[HTTPSRANDOMSIZE] = "1024"
	defaultValue[QUICMULTIPATH] = "0"
	defaultValue[QUICREQRESRUNTIME] = "30"

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
