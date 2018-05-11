from mpParam import MpParam

class MpParamXp(MpParam):

	RMEM       = "rmem"
	WMEM       = "wmem"
	SCHED      = "sched"
	SCHEDC     = "schedc"
	SCHEDS     = "scheds"
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
	HTTPFILE = "http_file"
	HTTPRANDOMSIZE = "http_file_size"
	SIRIRUNTIME = "siriRunTime"
	SIRIQUERYSIZE = "siriQuerySize"
	SIRIRESPONSESIZE = "siriResponseSize"
	SIRIDELAYQUERYRESPONSE = "siriDelayQueryResponse"
	SIRIMINPAYLOADSIZE = "siriMinPayloadSize"
	SIRIMAXPAYLOADSIZE = "siriMaxPayloadSize"
	SIRIINTERVALTIMEMS = "siriIntervalTimeMs"
	SIRIBUFFERSIZE = "siriBufferSize"
	SIRIBURSTSIZE = "siriBurstSize"
	SIRIINTERVALBURSTTIMEMS = "siriIntervalBurstTimeMs"
	MSGCLIENTSLEEP = "msgClientSleep"
	MSGSERVERSLEEP = "msgServerSleep"
	MSGNBREQUESTS = "msgNbRequests"
	MSGBYTES = "msgBytes"
	PRIOPATH0 = "prioPath0"
	PRIOPATH1 = "prioPath1"
	BACKUPPATH0 = "backupPath0"
	BACKUPPATH1 = "backupPath1"
	EXPIRATION = "expiration"
	BUFFERAUTOTUNING = "bufferAutotuning"
	METRIC = "metric"
	USEFASTJOIN = "useFastjoin"
	OPENBUP = "openBup"

	# global sysctl
	sysctlKey = {}
	sysctlKey[RMEM] = "net.ipv4.tcp_rmem"
	sysctlKey[WMEM] = "net.ipv4.tcp_wmem"
	sysctlKey[KERNELPM] = "net.mptcp.mptcp_path_manager"
	sysctlKey[SCHED] = "net.mptcp.mptcp_scheduler"
	sysctlKey[CC] = "net.ipv4.tcp_congestion_control"
	sysctlKey[AUTOCORK] = "net.ipv4.tcp_autocorking"
	sysctlKey[EARLYRETRANS] = "net.ipv4.tcp_early_retrans"
	sysctlKey[EXPIRATION] = "net.mptcp.mptcp_sched_expiration"
	sysctlKey[BUFFERAUTOTUNING] = "net.ipv4.tcp_moderate_rcvbuf"
	sysctlKey[USEFASTJOIN] = "net.mptcp.mptcp_use_fastjoin"


	sysctlKeyClient = {}
	sysctlKeyClient[KERNELPMC] = "net.mptcp.mptcp_path_manager"
	sysctlKeyClient[SCHEDC] = "net.mptcp.mptcp_scheduler"
	sysctlKeyServer = {}
	sysctlKeyServer[KERNELPMS] = "net.mptcp.mptcp_path_manager"
	sysctlKeyServer[SCHEDS] = "net.mptcp.mptcp_scheduler"

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
	defaultValue[EXPIRATION] = "300"
	defaultValue[BUFFERAUTOTUNING] = "1"
	defaultValue[METRIC] = "-1"
	defaultValue[USEFASTJOIN] = "1"

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
	defaultValue[HTTPFILE] = "random"
	defaultValue[HTTPRANDOMSIZE] = "1024"
	defaultValue[SIRIQUERYSIZE] = "2500"
	defaultValue[SIRIRESPONSESIZE] = "750"
	defaultValue[SIRIDELAYQUERYRESPONSE] = "0"
	defaultValue[SIRIMINPAYLOADSIZE] = "85"
	defaultValue[SIRIMAXPAYLOADSIZE] = "500"
	defaultValue[SIRIINTERVALTIMEMS] = "333"
	defaultValue[SIRIBUFFERSIZE] = "9"
	defaultValue[SIRIBURSTSIZE] = "0"
	defaultValue[SIRIINTERVALBURSTTIMEMS] = "0"
	defaultValue[MSGCLIENTSLEEP] = "5.0"
	defaultValue[MSGSERVERSLEEP] = "5.0"
	defaultValue[MSGNBREQUESTS] = "5"
	defaultValue[MSGBYTES] = "1200"
	defaultValue[PRIOPATH0] = "0"
	defaultValue[PRIOPATH1] = "0"
	defaultValue[BACKUPPATH0] = "0"
	defaultValue[BACKUPPATH1] = "0"

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
