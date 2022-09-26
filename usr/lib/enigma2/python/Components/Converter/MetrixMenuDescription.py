from Components.Converter.ConditionalShowHide import ConditionalShowHide
from Components.config import config


class MetrixMenuDescription(ConditionalShowHide):
	def __init__(self, argstr):
		ConditionalShowHide.__init__(self, argstr)
		self.show = config.plugins.MyMetrixLiteOther.menuDescription.value

	def calcVisibility(self):
		return self.show and ConditionalShowHide.calcVisibility(self)
