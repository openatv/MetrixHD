# IsSoftCSA Converter for Enigma2 Skins
# 
# This standalone converter can be used in skins to show/hide elements
# based on whether SoftCSA (software descrambling) is active.
#
# Works on both SoftCSA-enabled and standard Enigma2 builds:
# - On SoftCSA builds: Returns True when SW descrambling is active
# - On standard builds: Always returns False (element stays hidden)
#
# Usage in skin.xml:
#   <widget source="session.CurrentService" render="Pixmap" pixmap="softcsa.png" position="100,100" size="50,50">
#       <convert type="MetrixHDServiceInfo3"/>
#       <convert type="ConditionalShowHide"/>
#   </widget>
from enigma import iServiceInformation, iPlayableService

from Components.Converter.Converter import Converter
from Components.Element import cached


class MetrixHDServiceInfo3(Converter):
	def __init__(self, type):
		Converter.__init__(self, type)
		# Check once at init if SoftCSA is available in this build
		self._hasSoftCSA = hasattr(iServiceInformation, 'sIsSoftCSA')

	@cached
	def getBoolean(self):
		if not self._hasSoftCSA:
			return False
		
		service = self.source.service
		if service:
			info = service.info()
			if info:
				try:
					return info.getInfo(iServiceInformation.sIsSoftCSA) == 1
				except:
					pass
		return False

	boolean = property(getBoolean)

	def changed(self, what):
		if what[0] == self.CHANGED_SPECIFIC:
			if what[1] == iPlayableService.evUpdatedInfo:
				Converter.changed(self, what)
		elif what[0] != self.CHANGED_SPECIFIC:
			Converter.changed(self, what)
