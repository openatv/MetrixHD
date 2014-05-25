from Components.VariableText import VariableText
from enigma import eLabel
from Renderer import Renderer
from os import popen

class MetrixHDCPULoad(Renderer, VariableText):
	def __init__(self):
		Renderer.__init__(self)
		VariableText.__init__(self)
		
	GUI_WIDGET = eLabel

	def changed(self, what):
		if not self.suspended:
			loada = 0
			try:
				out_line = popen("cat /proc/loadavg").readline()
				loada = out_line[:4]	
			except:
				pass
			self.text = loada

	def onShow(self):
		self.suspended = False
		self.changed(None)

	def onHide(self):
		self.suspended = True
