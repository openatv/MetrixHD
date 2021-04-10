from Components.Converter.Converter import Converter
from Components.Element import cached


class MetrixHDEventName(Converter, object):
	NAME = 0
	SHORT_DESCRIPTION = 1
	EXTENDED_DESCRIPTION = 2
	ID = 3
	COMPLETE = 4

	def __init__(self, type):
		Converter.__init__(self, type)
		if type == "Description":
			self.type = self.SHORT_DESCRIPTION
		elif type == "ExtendedDescription":
			self.type = self.EXTENDED_DESCRIPTION
		elif type == "ID":
			self.type = self.ID
		elif type == "Complete":
			self.type = self.COMPLETE
		else:
			self.type = self.NAME

	@cached
	def getText(self):
		event = self.source.event
		if event is None:
			return ""

		if self.type == self.NAME:
			return event.getEventName()
		elif self.type == self.SHORT_DESCRIPTION:
			if event.getEventName() == event.getShortDescription():
				return ""
			else:
				return event.getShortDescription()
		elif self.type == self.EXTENDED_DESCRIPTION:
			return event.getExtendedDescription()
		elif self.type == self.ID:
			return str(event.getEventId())
		elif self.type == self.COMPLETE:
			if event.getEventName() == event.getShortDescription():
				return_str = event.getEventName()
			elif event.getShortDescription() == "":
				return_str = event.getEventName()
			else:
				return_str = event.getEventName() + ": " + event.getShortDescription()
			return return_str

	text = property(getText)
