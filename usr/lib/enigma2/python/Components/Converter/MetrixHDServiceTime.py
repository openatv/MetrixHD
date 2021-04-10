#taken from "ServicePosition" Converter
#edited by mogli123 @ et-view-support.com
from Components.Converter.Converter import Converter
from Components.Converter.Poll import Poll
from enigma import iPlayableService, iPlayableServicePtr, iServiceInformation, eTimer, eLabel
from Components.Element import cached, ElementError
from time import localtime, strftime, time, gmtime, asctime
from Components.Sources.Clock import Clock


class MetrixHDServiceTime(Poll, Converter, object):
	TYPE_STARTTIME = 0
	TYPE_ENDTIME = 1

	def __init__(self, type):
		Poll.__init__(self)
		Converter.__init__(self, type)
		if type == "StartTime":
			self.type = self.TYPE_STARTTIME
		elif type == "EndTime":
			self.type = self.TYPE_ENDTIME
		else:
			raise ElementError("type must be {StartTime, EndTime} for MetrixHDServiceTime converter")
		self.poll_enabled = True

	def getSeek(self):
		s = self.source.service
		return s and s.seek()

	@cached
	def getPosition(self):
		seek = self.getSeek()
		if seek is None:
			return None
		pos = seek.getPlayPosition()
		if pos[0]:
			return 0
		return pos[1]

	@cached
	def getLength(self):
		seek = self.getSeek()
		if seek is None:
			return None
		length = seek.getLength()
		if length[0]:
			return 0
		return length[1]

	@cached
	def getText(self):
		seek = self.getSeek()
		if seek is None:
			return ""
		else:
			if self.type == self.TYPE_STARTTIME:
				return strftime("%H:%M", localtime(time() - (self.position / 90000)))
			elif self.type == self.TYPE_ENDTIME:
				return strftime("%H:%M", localtime(time() + (self.length / 90000 - self.position / 90000)))

	range = 10000
	position = property(getPosition)
	length = property(getLength)
	text = property(getText)

	def changed(self, what):
		cutlist_refresh = what[0] != self.CHANGED_SPECIFIC or what[1] in (iPlayableService.evCuesheetChanged,)
		time_refresh = what[0] == self.CHANGED_POLL or what[0] == self.CHANGED_SPECIFIC and what[1] in (iPlayableService.evCuesheetChanged,)
		if time_refresh:
			self.downstream_elements.changed(what)
