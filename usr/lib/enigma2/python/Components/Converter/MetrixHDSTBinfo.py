from __future__ import division
from Components.Converter.Converter import Converter
from Components.config import config
from Components.Element import cached
from Components.Language import language
from os import path, popen, environ
from Plugins.Extensions.MyMetrixLite.__init__ import initOtherConfig
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import Screens.Standby
import gettext
import six
#from time import time

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("MyMetrixLite", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/MyMetrixLite/locale/"))

TEMPSIGN = '°C' if six.PY3 else str('\xc2\xb0C')


def _(txt):
	t = gettext.dgettext("MyMetrixLite", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t


initOtherConfig()


class MetrixHDSTBinfo(Converter, object):

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
		elif self.type == "MyMetrixConfig":
			return self.getMyMetrixConfig()
		elif self.type == "FLASHfree":
			return self.getFLASHfree()
		elif self.type == "CPUspeed":
			return self.getCPUspeed()
		return ""

	def getMyMetrixConfig(self):
		#stime = time()
		info = ""
		try:
			space = " " * int(config.plugins.MyMetrixLiteOther.STBDistance.value)
			if config.plugins.MyMetrixLiteOther.showCPULoad.value:
				info += self.getCPUload()
			if config.plugins.MyMetrixLiteOther.showRAMfree.value:
				info += space + self.getRAMfree()
			if config.plugins.MyMetrixLiteOther.showCPUTemp.value:
				info += space + self.getCPUtemp()
			if config.plugins.MyMetrixLiteOther.showSYSTemp.value:
				info += space + self.getSYStemp()
		except:
			pass
		#etime = time()
		#info += space + "Time: " + str(int(float(etime - stime)*1000)) + " ms"
		return info

	def getCPUload(self):
		info = ""
		if path.exists('/proc/loadavg'):
			f = open('/proc/loadavg', 'r')
			temp = f.readline(4)
			f.close()
			#info = "CPU-Load: " + temp
			info = temp.replace('\n', '').replace(' ', '')
			info = _("CPU-Load: %s") % info
		return info

	def getCPUtemp(self):
		info = ""
		temp = ""
		if path.exists('/proc/stb/fp/temp_sensor_avs'):
			f = open('/proc/stb/fp/temp_sensor_avs', 'r')
			temp = f.readline()
			f.close()
		elif path.exists('/proc/stb/power/avs'):
			f = open('/proc/stb/power/avs', 'r')
			temp = f.readline()
			f.close()
		elif path.exists('/proc/hisi/msp/pm_cpu'):
			try:
				for line in open('/proc/hisi/msp/pm_cpu').readlines():
					line = [x.strip() for x in line.strip().split(":")]
					if line[0] in ("Tsensor"):
						temp = line[1].split("=")
						temp = line[1].split(" ")
						temp = temp[2]
			except:
				temp = ""
		elif path.exists('/sys/devices/virtual/thermal/thermal_zone0/temp'):
			try:
				f = open('/sys/devices/virtual/thermal/thermal_zone0/temp', 'r')
				temp = f.read()
				temp = temp[:-4]
				f.close()
			except:
				temp = ""
		if temp and int(temp.replace('\n', '')) > 0:
			#info ="CPU-Temp: " + temp.replace('\n', '')  + str('\xc2\xb0') + "C"
			info = temp.replace('\n', '').replace(' ', '') + TEMPSIGN
			info = _("CPU-Temp: %s") % info
		return info

	def getSYStemp(self):
		info = ""
		temp = ""
		if path.exists('/proc/stb/sensors/temp0/value'):
			f = open('/proc/stb/sensors/temp0/value', 'r')
			temp = f.readline()
			f.close()
		elif path.exists('/proc/stb/fp/temp_sensor'):
			f = open('/proc/stb/fp/temp_sensor', 'r')
			temp = f.readline()
			f.close()
		elif path.exists('/proc/stb/sensors/temp/value'):
			f = open('/proc/stb/sensors/temp/value', 'r')
			temp = f.readline()
			f.close()
		if temp and int(temp.replace('\n', '')) > 0:
			#info ="SYS-Temp: " + temp.replace('\n', '') + str('\xc2\xb0') + "C"
			info = temp.replace('\n', '').replace(' ', '') + TEMPSIGN
			info = _("SYS-Temp: %s") % info
		return info

	def getRAMfree(self):
		info = ""
		if path.exists('/proc/meminfo'):
			f = open('/proc/meminfo', 'r')
			temp = f.readlines()
			f.close()
			try:
				for lines in temp:
					lisp = lines.split()
					if lisp[0] == "MemFree:":
						#info = "RAM-Free: " + str(int(lisp[1]) / 1024) + " MB"
						info = str(int(lisp[1]) // 1024)
						info = _("RAM-Free: %s MB") % info
						break
			except:
				pass
		return info

	def getFLASHfree(self):
		info = ""
		cmd = 'df -m'
		try:
			temp = popen(cmd).readlines()
			for lines in temp:
				lisp = lines.split()
				if lisp[5] == "/":
					#info = "Flash Memory free: " + lisp[3] + " MByte"
					info = lisp[3].replace(' ', '')
					info = _("Flash Memory free: %s MByte") % info
					break
		except:
			pass
		return info

	def getCPUspeed(self):
		info = ""
		if path.exists('/proc/cpuinfo'):
			f = open('/proc/cpuinfo', 'r')
			temp = f.readlines()
			f.close()
			try:
				for lines in temp:
					lisp = lines.split(': ')
					if lisp[0].startswith('cpu MHz'):
						#info = "CPU-Speed: " +  str(int(float(lisp[1].replace('\n', '')))) + " MHz"
						info = str(int(float(lisp[1].replace('\n', ''))))
						info = _("CPU-Speed: %s MHz") % info
						break
			except:
				pass
		return info

	text = property(getText)
