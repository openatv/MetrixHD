from Components.Converter.ServiceInfo import ServiceInfo
from Components.Element import cached


class MetrixHDServiceInfo(ServiceInfo):
	def __init__(self, argument):
		ServiceInfo.__init__(self, argument)

	@cached
	def getText(self):
		result = ServiceInfo.getText(self)
		if result and self.token == self.VIDEO_INFORMATION:
			result = result.replace("Hz", "").replace(" ", "")
		return result

	text = property(getText)
