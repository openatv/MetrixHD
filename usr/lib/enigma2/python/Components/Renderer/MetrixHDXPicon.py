##
## Picon renderer by Gruffy .. some speedups by Ghost
## XPicon mod by iMaxxx
##
from re import sub
from unicodedata import normalize
from six import PY2, text_type
from enigma import ePixmap

from PIL import Image, ImageFile, PngImagePlugin, ImageEnhance

from Components.config import config
from Components.Renderer.Renderer import Renderer
from ServiceReference import ServiceReference
from Tools.Directories import fileExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename
from Plugins.Extensions.MyMetrixLite.__init__ import initOtherConfig

initOtherConfig()


def patched_chunk_tRNS(self, pos, len):
	i16 = PngImagePlugin.i16
	s = ImageFile._safe_read(self.fp, len)
	if self.im_mode == "P":
		self.im_info["transparency"] = map(ord, s)
	elif self.im_mode == "L":
		self.im_info["transparency"] = i16(s)
	elif self.im_mode == "RGB":
		self.im_info["transparency"] = i16(s), i16(s[2:]), i16(s[4:])
	return s


if PY2:
	PngImagePlugin.PngStream.chunk_tRNS = patched_chunk_tRNS


def patched_load(self):
	if self.im and self.palette and self.palette.dirty:
		apply(self.im.putpalette, self.palette.getdata())
		self.palette.dirty = 0
		self.palette.rawmode = None
		try:
			trans = self.info["transparency"]
		except KeyError:
			self.palette.mode = "RGB"
		else:
			try:
				for i, a in enumerate(trans):
					self.im.putpalettealpha(i, a)
			except TypeError:
				self.im.putpalettealpha(trans, 0)
			self.palette.mode = "RGBA"
	if self.im:
		return self.im.pixel_access(self.readonly)


if PY2:
	Image.Image.load = patched_load


class MetrixHDXPicon(Renderer):
	searchPaths = ('/media/mmc/%s/', '/media/usb/XPicons/%s/', '/media/usb/%s/', '/%s/', '/%sx/', '/usr/share/enigma2/XPicons/%s/', '/usr/share/enigma2/%s/', '/usr/%s/', '/media/hdd/XPicons/%s/', '/media/hdd/%s/')

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
				if sname.count(':') > 9:
					sname = '_'.join(sname.split(':')[0:10])
				pngname = self.nameCache.get(sname, "")
				if not pngname or not fileExists(pngname):
					pngname = self.findPicon(sname)
					if not pngname:
						fields = sname.split('_')
						if len(fields) == 10:
							if not fields[6].endswith('0000'):
								no_subnet = "%s_%s_%s" % ('_'.join(fields[:6]), fields[6][:-4] + '0000', '_'.join(fields[7:]))
								pngname = self.findPicon(no_subnet)			# removed SubNetwork in the right part of the NameSpace field
							if not pngname and fields[0] != '1':
								fields[0] = '1'
								pngname = self.findPicon('_'.join(fields))  # fallback to 1 for online streams (4097, 5001, 5002; 5003, etc.)
							if not pngname and fields[2] != '2':
								fields[2] = '1'
								pngname = self.findPicon('_'.join(fields))  # fallback to 1 for online streams + find an picon with undefined stream quality
					if not pngname:		# search picon by channel name
						name = ServiceReference(self.source.text).getServiceName()
						name = normalize('NFKD', text_type(name))
						name = sub('[^a-z0-9]', '', name.replace('&', 'and').replace('+', 'plus').replace('*', 'star').lower())
						if len(name) > 0:
							pngname = self.findPicon(name)
							if not pngname and len(name) > 2 and name.endswith('hd'):
								pngname = self.findPicon(name[:-2])
					if pngname != "" and sname.split('_', 1)[0] == "1":
						self.nameCache[sname] = pngname
				if not pngname:			# no picon for service found
					pngname = self.nameCache.get("default", "")
					if not pngname:		# no default yet in cache...
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
						except:
							print("[MetrixHDXPicon] cant load image: %s" % pngname)
							tmp = resolveFilename(SCOPE_CURRENT_SKIN, "picon_default.png")
							if fileExists(tmp):
								pngname = tmp
							else:
								pngname = resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/picon_default.png")
							im = Image.open(pngname).convert('RGBA')
						imw, imh = im.size
						inh = self.instance.size().height()
						if imh != inh:
							sf = float(inh) / imh
							im = im.resize((int(imw * sf), int(imh * sf)), Image.ANTIALIAS)
							ims = ImageEnhance.Sharpness(im)
							im = ims.enhance(float(config.plugins.MyMetrixLiteOther.piconsharpness_experimental.value))
							tempfile = '/tmp/picon.png'
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

	def findPicon(self, serviceName):
		for path in self.searchPaths:
			pngname = (path % self.path) + serviceName + ".png"
			if fileExists(pngname):
				return pngname
		return ""
