from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from subprocess import Popen, PIPE

class MpMininetBuilder(Topo):
	def __init__(self):
		Topo.__init__( self )
		self.net = None

	def commandTo(self, who, cmd):
		return who.cmd(cmd)

	def notNSCommand(self, cmd):
		p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
		stdout, stderr = p.communicate()
		if stderr:
			return "Error"
		return stdout

	def startNetwork(self):
		self.net = Mininet(topo=self,link=TCLink)
		self.net.start()

	def getCLI(self):
		if self.net is None:
			print("Can not get the CLI")
		else:
			CLI(self.net)

	def getHost(self, who):
		if self.net is None:
			print("Network not available....")
			raise Exception("Network not ready");
		else:
			return self.net.getNodeByName(who)

	def stopNetwork(self):
		if self.net is None:
			print("Could not stop network... Nothing to stop)")
		else:
			self.net.stop()
