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
	PVRATELIMIT= "pvRateLimit"
	PVG        = "pvG" #patched version of pv
	PVZ        = "pvZ"
	NCSERVERPORT = "ncServerPort"
	NCCLIENTPORT = "ncClientPort"
	CHANGEPV   = "changePv"
	CHANGEPVAT = "changePvAt"
	HTTPSFILE  = "file" # file to wget, if random : we create a file with random data called random.
	HTTPSRANDOMSIZE = "file_size" # if file is set to random, define the size of the random file
	EPLOADTESTDIR = "epload_test_dir"
	HTTPFILE = "http_file"
	HTTPRANDOMSIZE = "http_file_size"
	NETPERFTESTLEN = "netperfTestlen"
	NETPERFTESTNAME = "netperfTestname"
	NETPERFREQRESSIZE = "netperfReqresSize"
	ABCONCURRENTREQUESTS = "abConccurentRequests"
	ABTIMELIMIT = "abTimelimit"
	SIRIRUNTIME = "siriRunTime"
	SIRIQUERYSIZE = "siriQuerySize"
	SIRIRESPONSESIZE = "siriResponseSize"
	SIRIDELAYQUERYRESPONSE = "siriDelayQueryResponse"
	SIRIMINPAYLOADSIZE = "siriMinPayloadSize"
	SIRIMAXPAYLOADSIZE = "siriMaxPayloadSize"
	SIRIINTERVALTIMEMS = "siriIntervalTimeMs"
	SIRIBUFFERSIZE = "siriBufferSize"
	VLCFILE = "vlcFile"
	VLCTIME = "vlcTime"
	DITGKBYTES = "ditgKBytes"
	DITGMEANPOISSONPACKETSSEC = "ditgMeanPoissonPacketsSec"
	BURSTSONPACKETSSEC = "burstsOnPacketsSec"
	BURSTSOFFPACKETSSEC = "burstsOffPacketsSec"
	PRIOPATH0 = "prioPath0"
	PRIOPATH1 = "prioPath1"
	BACKUPPATH0 = "backupPath0"
	BACKUPPATH1 = "backupPath1"
	EXPIRATION = "expiration"
	METRIC = "metric"


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
	defaultValue[EXPIRATION] = "300"
	defaultValue[METRIC] = "-1"

	defaultValue[CLIENTPCAP] = "no"
	defaultValue[SERVERPCAP] = "no"
	defaultValue[SNAPLENPCAP] = "65535"  # Default snapping value of tcpdump
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
	defaultValue[EPLOADTESTDIR] = "/bla/bla/bla"
	defaultValue[HTTPFILE] = "random"
	defaultValue[HTTPRANDOMSIZE] = "1024"
	defaultValue[NETPERFTESTLEN] = "10"
	defaultValue[NETPERFTESTNAME] = "TCP_RR"
	defaultValue[NETPERFREQRESSIZE] = "2K,256"
	defaultValue[ABCONCURRENTREQUESTS] = "50"
	defaultValue[ABTIMELIMIT] = "20"
	defaultValue[SIRIQUERYSIZE] = "2500"
	defaultValue[SIRIRESPONSESIZE] = "750"
	defaultValue[SIRIDELAYQUERYRESPONSE] = "0"
	defaultValue[SIRIMINPAYLOADSIZE] = "85"
	defaultValue[SIRIMAXPAYLOADSIZE] = "500"
	defaultValue[SIRIINTERVALTIMEMS] = "333"
	defaultValue[SIRIBUFFERSIZE] = "9"
	defaultValue[VLCFILE] = "bunny_ibmff_360.mpd"
	defaultValue[VLCTIME] = "0"
	defaultValue[DITGKBYTES] = "10000"
	defaultValue[DITGMEANPOISSONPACKETSSEC] = "1500"
	defaultValue[BURSTSONPACKETSSEC] = "2250"
	defaultValue[BURSTSOFFPACKETSSEC] = "750"
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
