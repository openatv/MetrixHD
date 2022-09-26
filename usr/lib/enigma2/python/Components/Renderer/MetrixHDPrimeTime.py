from datetime import datetime
from time import localtime, mktime, time
from enigma import eLabel, eEPGCache

from Components.config import config
from Components.Renderer.Renderer import Renderer
from Components.VariableText import VariableText


class MetrixHDPrimeTime(Renderer, VariableText):

	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)
		self.epgcache = eEPGCache.getInstance()

	GUI_WIDGET = eLabel

	def changed(self, what):
		event = self.source.event

		if event is None:
			self.text = ""
			return

		service = self.source.service
		text = ""
		evt = None

		if self.epgcache is not None:
			evt = self.epgcache.lookupEvent(['IBDCT', (service.toString(), 0, -1, -1)])
		if evt:
			now = localtime(time())
			try:
				hour, minute = config.epgselection.graph_primetimehour.value, config.epgselection.graph_primetimemins.value
			except:
				hour, minute = 20, 15
			dt = datetime(now.tm_year, now.tm_mon, now.tm_mday, hour, minute)
			primetime = int(mktime(dt.timetuple()))
			next = False
			for x in evt:
				if x[4]:
					begin = x[1]
					end = x[1] + x[2]
					if begin <= primetime and end > primetime or next:
						if not next and end <= primetime + 1200:  # 20 mins tolerance to starting next event
							next = True
							continue
						t = localtime(begin)
						text = text + "%02d:%02d %s\n" % (t[3], t[4], x[4])
						break
					if begin > primetime:  # entry > primetime ? -> primetime not in epg
						text = text + "n/a"
						break
				else:
					text = text + "n/a"
					break

		self.text = text
