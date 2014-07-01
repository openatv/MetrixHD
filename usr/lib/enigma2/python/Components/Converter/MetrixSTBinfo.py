from Components.Converter.Converter import Converter
from Components.config import config
from Components.Element import cached
from os import path
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
		elif self.type == "CPUtemp":
			return self.getCPUtemp()
		elif self.type == "SYStemp":
			return self.getSYStemp()
		elif self.type =="MyMetrixConfig":
			return self.getMyMetrixConfig()
		else:
			return ""

	def getMyMetrixConfig(self):
		info = ""
		space = "        "
		if config.plugins.MyMetrixLiteOther.showCPULoad.getValue() is not False:
			info += self.getCPUload()
		if config.plugins.MyMetrixLiteOther.showCPUTemp.getValue() is not False:
			info += space + self.getCPUtemp()
		if config.plugins.MyMetrixLiteOther.showSYSTemp.getValue() is not False:
			info += space + self.getSYStemp()
		return info

	def getCPUload(self):
		info = ""
		temp = ""
		if path.exists('/proc/loadavg'):
			f = open('/proc/loadavg', 'r')
			temp = f.read()
			f.close()
			info = "CPU-Load:  " + str(temp[:4])
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
			info ="CPU-Temp:  " + temp.replace('\n', '')  + str('\xc2\xb0') + "C"
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
			info ="SYS-Temp:  " + temp.replace('\n', '') + str('\xc2\xb0') + "C"
		else:
			info = ""
		return info

	text = property(getText)

