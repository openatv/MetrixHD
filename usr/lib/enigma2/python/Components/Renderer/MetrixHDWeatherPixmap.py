# by nikolasi for MetrixHD
#    <widget source="session.CurrentService" render="MetrixHDWeatherPixmap" position="156,50" size="50,50" alphatest="blend" zPosition="9">
#        <convert type="MetrixHDWeather">currentWeatherCode</convert>
#    </widget>
from Renderer import Renderer 
from enigma import ePixmap, ePicLoad
from Tools.Directories import fileExists, pathExists

lastPiconPath = None

class MetrixHDWeatherPixmap(Renderer):
	__module__ = __name__
	searchPaths = ('/media/usb/%s/', '/usr/share/enigma2/%s/', '/media/hdd/%s/')

	def __init__(self):
		Renderer.__init__(self)
		self.path = 'piconMSNWeather'
		self.pngname = ""

	def applySkin(self, desktop, parent):
		attribs = []
		for (attrib, value,) in self.skinAttributes:
			if attrib == "path":
				self.path = value
			else:
				attribs.append((attrib, value))

		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap

	def changed(self, what):
		if self.instance:
			sname = ''
			if (what[0] != self.CHANGED_CLEAR):
				sname = self.ConvertCondition(self.source.text)
				pngname = self.findPicon(sname)
				if self.pngname != pngname:
					if pngname:
						self.instance.setScale(1)
						self.instance.setPixmapFromFile(pngname)
						self.instance.show()
					else:
						self.instance.hide()
					self.pngname = pngname

	def findPicon(self, serviceName):
		global lastPiconPath
		if lastPiconPath is not None:
			pngname = lastPiconPath + serviceName + ".png"
			if pathExists(pngname):
				return pngname
			else:
				return ""
		else:
			pngname = ""
			for path in self.searchPaths:
				if pathExists((path % self.path)):
					pngname = (path % self.path) + serviceName + ".png"
					if pathExists(pngname):
						lastPiconPath = (path % self.path)
						break
			if pathExists(pngname):
				return pngname
			else:
				return ""

	def ConvertCondition(self, c):
		condition = "NA"
		if c == "S":
			condition = "0"
		elif c == "Z":
			condition = "3"
		elif c == "U":
			condition = "5"
		elif c == "G":
			condition = "8"
		elif c == "Q":
			condition = "9"
		elif c == "R":
			condition = "11"
		elif c == "W":
			condition = "13"
		elif c == "X":
			condition = "17"
		elif c == "F":
			condition = "19"
		elif c == "L":
			condition = "20"
		elif c == "S":
			condition = "23"
		elif c == "N":
			condition = "26"
		elif c == "I":
			condition = "27"
		elif c == "H":
			condition = "28"
		elif c == "C":
			condition = "31"
		elif c == "B":
			condition = "32"
		elif c == "B":
			condition = "36"
		elif c == "0":
			condition = "37"
		elif c == 49:
			condition = "NA"
		else:
			condition = "NA"
		return str(condition)
