##
## Picon renderer by Gruffy .. some speedups by Ghost
## XPicon mod by iMaxxx
##
from os.path import exists
from enigma import ePixmap

from PIL import Image, ImageFile, ImageEnhance

from Components.config import config
from Components.Renderer.Picon import getPiconName
from Components.Renderer.Renderer import Renderer
from Tools.Directories import SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename
from Plugins.Extensions.MyMetrixLite.__init__ import initOtherConfig

initOtherConfig()


class MetrixHDXPicon(Renderer):

	def __init__(self):
		Renderer.__init__(self)
		self.path = "picon"
		self.nameCache = {}
		self.pngname = ""

	def applySkin(self, desktop, parent):
		attribs = []
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
				if sname.count(":") > 9:
					snameN = "_".join(sname.split(":")[0:10])
					pngname = self.nameCache.get(snameN, "")
				if not pngname or not exists(pngname):
					pngname = getPiconName(sname)
					if pngname != "" and sname.split("_", 1)[0] == "1":
						self.nameCache[sname] = pngname
				if not pngname:			# no picon for service found
					pngname = self.nameCache.get("default", "")
					if not pngname:		# no default yet in cache...
						tmp = resolveFilename(SCOPE_CURRENT_SKIN, "picon_default.png")
						pngname = tmp if exists(tmp) else resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/picon_default.png")
						self.nameCache["default"] = pngname
				if self.pngname != pngname:
					if config.plugins.MyMetrixLiteOther.piconresize_experimental.value:
						try:
							ImageFile.LOAD_TRUNCATED_IMAGES = True
							im = Image.open(pngname).convert("RGBA")
						except Exception:
							print(f"[MetrixHDXPicon] cant load image: {pngname}")
							tmp = resolveFilename(SCOPE_CURRENT_SKIN, "picon_default.png")
							pngname = tmp if exists(tmp) else resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/picon_default.png")
							im = Image.open(pngname).convert("RGBA")
						imw, imh = im.size
						inh = self.instance.size().height()
						if imh != inh:
							sf = float(inh) / imh
							im = im.resize((int(imw * sf), int(imh * sf)), Image.ANTIALIAS)
							ims = ImageEnhance.Sharpness(im)
							im = ims.enhance(float(config.plugins.MyMetrixLiteOther.piconsharpness_experimental.value))
							tempfile = "/tmp/picon.png"
							im.save(tempfile)
							self.instance.setPixmapFromFile(tempfile)
						else:
							self.instance.setPixmapFromFile(pngname)
					else:
						self.instance.setPixmapFromFile(pngname)
					self.instance.setScale(1)
					self.pngname = pngname
			else:
				self.pngname = ""
				self.instance.hide()
