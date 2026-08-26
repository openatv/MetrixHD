##
## Picon renderer by Gruffy .. some speedups by Ghost
## XPicon mod by iMaxxx
##
from os.path import exists, getmtime, getsize
from enigma import ePixmap, eServiceReference, iServiceInformation

from PIL import Image, ImageFile, ImageEnhance

from Components.config import config
from Components.Renderer.Picon import getPiconName
from Components.Renderer.Renderer import Renderer
import NavigationInstance
from Tools.Directories import SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename
from Plugins.Extensions.MyMetrixLite.__init__ import initOtherConfig


class MetrixHDXPicon(Renderer):

	def __init__(self):
		Renderer.__init__(self)
		self.path = "picon"
		self.nameCache = {}
		self.pngname = ""
		if not hasattr(config.plugins, "MyMetrixLiteOther"):  # This is for other skins
			initOtherConfig()

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

	def getDABImage(self, serviceRef):
		ref = eServiceReference(serviceRef or "")
		if ref.type != eServiceReference.idServiceDAB or NavigationInstance.instance is None:
			return ""
		playingRef = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
		if not playingRef or playingRef.toString().split(":", 10)[:10] != ref.toString().split(":", 10)[:10]:
			return ""
		service = NavigationInstance.instance.getCurrentService()
		info = service and service.info()
		image = info and info.getInfoString(iServiceInformation.sTagImage) or ""
		return image if image and exists(image) else ""

	def changed(self, what):
		if self.instance:
			pngname = ""
			if what[0] != self.CHANGED_CLEAR:
				self.instance.show()
				sname = self.source.text
				pngname = self.getDABImage(sname)
				if not pngname and sname.count(":") > 9:
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
				pngkey = (pngname, getmtime(pngname), getsize(pngname)) if pngname and exists(pngname) else pngname
				if self.pngname != pngkey:
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
							im = im.resize((int(imw * sf), int(imh * sf)), Image.LANCZOS)
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
					self.pngname = (pngname, getmtime(pngname), getsize(pngname)) if pngname and exists(pngname) else pngname
			else:
				self.pngname = ""
				self.instance.hide()
