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
		text = ""
		if event and self.epgcache:
			service = self.source.service
			now = localtime(time())
			try:
				hour, minute = config.epgselection.graph_primetimehour.value, config.epgselection.graph_primetimemins.value
			except Exception:
				hour, minute = 20, 15
			dt = datetime(now.tm_year, now.tm_mon, now.tm_mday, hour, minute)
			primetime = int(mktime(dt.timetuple()))
			evt = self.epgcache.lookupEvent(['IBDTZ', (service.toString(), 0, primetime, 0)])
			if evt:
				x = evt[0]
				t = localtime(x[1])
				text = "%02d:%02d %s" % (t[3], t[4], x[3])
			else:
				text = "n/a"

		self.text = text
