from __future__ import print_function
##
## Picon renderer by Gruffy .. some speedups by Ghost
## XPicon mod by iMaxxx
##
from Components.Renderer.Renderer import Renderer
from enigma import ePixmap
from enigma import iServiceInformation, iPlayableService, iPlayableServicePtr
from Tools.Directories import fileExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename
from Plugins.Extensions.MyMetrixLite.__init__ import initOtherConfig
from Components.config import config
from PIL import Image, ImageFile, PngImagePlugin, ImageEnhance
import six

initOtherConfig()

# For SNP
from ServiceReference import ServiceReference
import re, unicodedata

class MetrixHDXPicon(Renderer):
	searchPaths = ('/media/mmc/%s/', '/media/usb/XPicons/%s/', '/media/usb/%s/', '/%s/', '/%sx/', '/usr/share/enigma2/XPicons/%s/', '/usr/share/enigma2/%s/', '/usr/%s/', '/media/hdd/XPicons/%s/', '/media/hdd/%s/')

	def __init__(self):
		Renderer.__init__(self)
		self.path = "picon"
		self.nameCache = { }
		self.pngname = ""

	def applySkin(self, desktop, parent):
		attribs = [ ]
		for (attrib, value) in self.skinAttributes:
			if attrib == "path":
				self.path = value
			else:
				attribs.append((attrib, value))
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap

	def changed(self, what):
		if self.instance:
			pngname = ""
			if what[0] != self.CHANGED_CLEAR:
				self.instance.show()
				sname = self.source.text
				pos = sname.rfind(':')
				if pos != -1:
					sname = sname[:pos].rstrip(':').replace(':', '_')
					sname = sname.split("_http")[0]
				pngname = self.nameCache.get(sname, "")
				if pngname == "" or not fileExists(pngname):
					pngname = self.findPicon(sname)
					if pngname == "":
						fields = sname.split('_', 3)
						if len(fields) > 0 and fields[0] != '1':                    #fallback to 1 for IPTV streams
							fields[0] = '1'
							pngname = self.findPicon('_'.join(fields))
						if pngname == "" and len(fields) > 2 and fields[2] != '2':  #fallback to 1 for find picons with not defined stream quality
							fields[2] = '1'
							pngname = self.findPicon('_'.join(fields))
					if not pngname: # picon by channel name
						name = ServiceReference(self.source.text).getServiceName()
						name = unicodedata.normalize('NFKD', six.text_type(name))
						name = re.sub('[^a-z0-9]', '', name.replace('&', 'and').replace('+', 'plus').replace('*', 'star').lower())
						if len(name) > 0:
							pngname = self.findPicon(name)
							if not pngname and len(name) > 2 and name.endswith('hd'):
								pngname = self.findPicon(name[:-2])
					if pngname != "" and sname.split('_', 1)[0] == "1":
						self.nameCache[sname] = pngname
				if pngname == "": # no picon for service found
					pngname = self.nameCache.get("default", "")
					if pngname == "": # no default yet in cache..
						pngname = self.findPicon("picon_default")
						if pngname == "":
							tmp = resolveFilename(SCOPE_CURRENT_SKIN, "picon_default.png")
							if fileExists(tmp):
								pngname = tmp
							else:
								pngname = resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/picon_default.png")
						self.nameCache["default"] = pngname
				if self.pngname != pngname:
					if config.plugins.MyMetrixLiteOther.piconresize_experimental.value:
						try:
							ImageFile.LOAD_TRUNCATED_IMAGES = True
							im = Image.open(pngname).convert('RGBA')
							imw, imh = im.size
							inh = self.instance.size().height()
							if imh != inh:
								sf = float(inh)/imh
								im = im.resize((int(imw*sf), int(imh*sf)), Image.ANTIALIAS)
								ims = ImageEnhance.Sharpness(im)
								im = ims.enhance(float(config.plugins.MyMetrixLiteOther.piconsharpness_experimental.value))
								tempfile = '/tmp/picon.png'
								im.save(tempfile)
								self.instance.setPixmapFromFile(tempfile)
							else:
								self.instance.setPixmapFromFile(pngname)
						except:
							self.instance.setPixmapFromFile(pngname)
					else:
						self.instance.setPixmapFromFile(pngname)
					self.instance.setScale(1)
					self.pngname = pngname
			else:
				self.pngname = ""
				self.instance.hide()

	def findPicon(self, serviceName):
		for path in self.searchPaths:
			pngname = (path % self.path) + serviceName + ".png"
			if fileExists(pngname):
				return pngname
		return ""
