# by nikolasi for MetrixHD
#    <widget source="session.CurrentService" render="MetrixHDWeatherPixmap" position="156,50" size="50,50" alphatest="blend" zPosition="9">
#        <convert type="MetrixHDWeather">currentWeatherCode</convert>
#    </widget>
from os import listdir
from os.path import exists, join as pathjoin, isfile
from enigma import ePixmap, eTimer
from Components.config import config
from Components.Renderer.Renderer import Renderer
from Tools.LoadPixmap import LoadPixmap


class MetrixHDWeatherPixmap(Renderer):
	__module__ = __name__
	searchPaths = ('/usr/share/enigma2/MetrixHD/%s/', '/usr/share/enigma2/%s/', '/media/hdd/%s/', '/media/usb/%s/')

	def __init__(self):
		Renderer.__init__(self)
		self.path = 'animated_weather_icons'
		self.pixdelay = 100
		self.pixdelay_overwrite = False
		self.slideicon = None
		self.winddiricon = None
		self.iconpath = config.plugins.MetrixWeather.iconpath.value
		if not exists(self.iconpath) and config.plugins.MetrixWeather.type == "2":
			self.iconpath = None

	def applySkin(self, desktop, parent):
		attribs = []
		for (attrib, value,) in self.skinAttributes:
			if attrib == "path":
				self.path = value
			elif attrib == "pixdelay":
				self.pixdelay = int(value)
				self.pixdelay_overwrite = True
			else:
				attribs.append((attrib, value))

		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap

	def changed(self, what):
		if self.instance:
			sname = ''
			if (what[0] != self.CHANGED_CLEAR):
				if config.plugins.MetrixWeather.type == "0":
					return
				sname = self.source.text
				if self.iconpath:
					imgpath = pathjoin(self.iconpath, '%s.png' % sname)
					if isfile(imgpath):
						self.instance.setPixmap(imgpath)
					return
				for path in self.searchPaths:
					if exists((path % self.path)):
						self.runAnim(sname)

	def runAnim(self, id):
		global total
		animokicon = False
		for path in self.searchPaths:
			if exists('%s%s' % ((path % self.path), id)):
				pathanimicon = '%s%s/a' % ((path % self.path), id)
				path2 = '%s%s' % ((path % self.path), id)
				dir_work = listdir(path2)
				total = len(dir_work)
				self.slideicon = total
				animokicon = True
			else:
				if exists('%sNA' % (path % self.path)):
					pathanimicon = '%sNA/a' % (path % self.path)
					path2 = '%sNA' % (path % self.path)
					dir_work = listdir(path2)
					total = len(dir_work)
					self.slideicon = total
					animokicon = True
		if animokicon == True:
			self.picsicon = []
			for x in range(self.slideicon):
				self.picsicon.append(LoadPixmap("%s%s.png" % (pathanimicon, str(x))))

			if not self.pixdelay_overwrite:
				self.pixdelay = int(config.plugins.MetrixWeather.animationspeed.value)
			self.timericon = eTimer()
			self.timericon.callback.append(self.timerEvent)
			self.timerEvent()
			#self.timericon.start(self.pixdelay, True)

	def timerEvent(self):
		if self.slideicon == 0:
			self.slideicon = total
		if self.slideicon > total:
			self.slideicon = total
		self.timericon.stop()
		self.instance.setScale(1)
		try:
			self.instance.setPixmap(self.picsicon[self.slideicon - 1])
		except Exception:
			pass
		self.slideicon = self.slideicon - 1
		if self.pixdelay:
			self.timericon.start(self.pixdelay, True)
