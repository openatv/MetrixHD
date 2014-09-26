from Components.Converter.Converter import Converter
from Components.config import config
from Components.Element import cached
from os import path, popen
from Plugins.Extensions.MyMetrixLite.__init__ import initOtherConfig
import Screens.Standby

initOtherConfig()

class MetrixSTBinfo(Converter, object):

	def __init__(self, type):
		Converter.__init__(self, type)
		self.type = type

	@cached
	def getText(self):
		if Screens.Standby.inStandby:
			return ""
		elif self.type == "CPUload":
			return self.getCPUload()
		elif self.type == "RAMfree":
			return self.getRAMfree()
		elif self.type == "CPUtemp":
			return self.getCPUtemp()
		elif self.type == "SYStemp":
			return self.getSYStemp()
		elif self.type =="MyMetrixConfig":
			return self.getMyMetrixConfig()
		elif self.type == "FLASHfree":
			return self.getFLASHfree()
		else:
			return ""

	def getMyMetrixConfig(self):
		info = ""
		space = "        "
		if config.plugins.MyMetrixLiteOther.showCPULoad.getValue() is True:
			info += self.getCPUload()
		if config.plugins.MyMetrixLiteOther.showRAMfree.getValue() is True:
			info += space + self.getRAMfree()
		if config.plugins.MyMetrixLiteOther.showCPUTemp.getValue() is True:
			info += space + self.getCPUtemp()
		if config.plugins.MyMetrixLiteOther.showSYSTemp.getValue() is True:
			info += space + self.getSYStemp()
		return info

	def getCPUload(self):
		info = ""
		temp = ""
		if path.exists('/proc/loadavg'):
			f = open('/proc/loadavg', 'r')
			temp = f.read()
			f.close()
			info = "CPU-load:  " + str(temp[:4])
		else:
			info = ""
		return info

	def getCPUtemp(self):
		info = ""
		temp = ""
		if path.exists('/proc/stb/fp/temp_sensor_avs'):
			f = open('/proc/stb/fp/temp_sensor_avs', 'r')
			temp = f.read()
			f.close()
		if temp and int(temp.replace('\n', '')) > 0:
			info ="CPU-temp:  " + temp.replace('\n', '')  + str('\xc2\xb0') + "C"
		else:
			info = ""
		return info

	def getSYStemp(self):
		info = ""
		temp = ""
		if path.exists('/proc/stb/sensors/temp0/value'):
			f = open('/proc/stb/sensors/temp0/value', 'r')
			temp = f.read()
			f.close()
		elif path.exists('/proc/stb/fp/temp_sensor'):
			f = open('/proc/stb/fp/temp_sensor', 'r')
			temp = f.read()
			f.close()
		if temp and int(temp.replace('\n', '')) > 0:
			info ="SYS-temp:  " + temp.replace('\n', '') + str('\xc2\xb0') + "C"
		else:
			info = ""
		return info

	def getRAMfree(self):
		info = ""
		cmd = 'free -m | grep "Mem:" | awk -F " " ' + "'{print $4}'"
		temp = popen(cmd).read()
		if temp:
			info = "RAM-free: " + temp.replace("\n", "") + " MB"
		return info

	def getFLASHfree(self):
		info = ""
		cmd = 'df -m | grep "rootfs" | awk -F " " ' + "'{print $4}'"
		temp = popen(cmd).read()
		if temp:
			info = "Available Flash Memory: " + temp.replace("\n", "") + " MByte"
		return info

	text = property(getText)

