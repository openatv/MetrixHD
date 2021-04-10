from Components.Converter.Converter import Converter
from Components.Element import cached


class MetrixHDConvEventName(Converter, object):
	NAME = 0
	SHORT_DESCRIPTION = 1
	EXTENDED_DESCRIPTION = 2
	ID = 3

	def __init__(self, type):
		Converter.__init__(self, type)
		if type == "Description":
			self.type = self.SHORT_DESCRIPTION
		elif type == "ExtendedDescription":
			self.type = self.EXTENDED_DESCRIPTION
		elif type == "ID":
			self.type = self.ID
		else:
			self.type = self.NAME

	@cached
	def getText(self):
		event = self.source.event
		if event is None:
			return ""

		if self.type == self.NAME:
			ret_str = event.getEventName()
		elif self.type == self.SHORT_DESCRIPTION:
			ret_str = event.getShortDescription()
		elif self.type == self.EXTENDED_DESCRIPTION:
			short_desc = event.getShortDescription()
			exten_desc = event.getExtendedDescription()
			if short_desc == "":
				ret_str = exten_desc
			elif exten_desc == "":
				ret_str = short_desc
			else:
				ret_str = short_desc + "\n\n" + exten_desc
		elif self.type == self.ID:
			ret_str = str(event.getEventId())

		return ret_str

	text = property(getText)
